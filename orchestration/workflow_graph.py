"""
WorkflowGraph — DAG-based multi-agent orchestrator.

Replaces the linear AgentOrchestrator with a fully addressable
directed acyclic graph that supports:

  - Sequential edges          A → B → C
  - Conditional edges         A → B (if fn) | A → C (else)
  - Fan-out (parallel paths)  A → [B, C]  (future async extension)
  - Named entry / exit nodes
  - Integrated StateManager checkpointing
  - Full OpenTelemetry pipeline trace
  - Mid-graph halt via node condition returning False
Usage
-----
    graph = (
        WorkflowGraph()
        .add_node("diag",   TestDiagnosticsAgent())
        .add_node("rca",    RootCauseAnalyzerAgent())
        .add_node("action", ActionPlannerAgent())
        .add_node("exec",   ExecutionAgent())
        .add_edge("diag",   "rca")
        .add_edge("rca",    "action")
        .add_edge("action", "exec")
        .set_entry("diag")
    )
    result = graph.run(initial_message)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import (
    Callable, Dict, List, Optional, Tuple, Union
)

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from agents.base_agent import BaseAgent, Message
from orchestration.state_manager import StateManager, ExecutionState
from utils.logger import get_logger

logger = get_logger("WorkflowGraph")
tracer = trace.get_tracer("WorkflowGraph")


# ---------------------------------------------------------------------------
# Edge & Node
# ---------------------------------------------------------------------------

@dataclass
class Edge:
    """
    Directed edge from one node to another.

    condition: optional callable (Message -> bool).
        If it returns False the edge is not followed.
    label:     human-readable tag (e.g. "high_confidence", "default")
    """
    target:    str
    condition: Optional[Callable[[Message], bool]] = None
    label:     str = "default"

    def is_passable(self, message: Message) -> bool:
        if self.condition is None:
            return True
        return self.condition(message)


@dataclass
class WorkflowNode:
    """
    A single node in the workflow DAG.

    agent:      BaseAgent instance to execute
    edges:      outgoing edges (supports multiple for fan-out / conditional)
    skip_if:    if this fn returns True the node is skipped entirely
    """
    name:    str
    agent:   BaseAgent
    edges:   List[Edge]           = field(default_factory=list)
    skip_if: Optional[Callable[[Message], bool]] = None


# ---------------------------------------------------------------------------
# WorkflowGraph
# ---------------------------------------------------------------------------

class WorkflowGraph:
    """
    Directed Acyclic Graph orchestrator.

    Quickstart
    ----------
    graph = (
        WorkflowGraph()
        .add_node("diag",   TestDiagnosticsAgent())
        .add_node("rca",    RootCauseAnalyzerAgent())
        .add_node("action", ActionPlannerAgent())
        .add_node("exec",   ExecutionAgent())
        .add_edge("diag",   "rca")
        .add_edge("rca",    "action")
        .add_edge("action", "exec",
                  condition=lambda m: m.content.get("confidence", 0) > 0.7,
                  label="high_confidence")
        .set_entry("diag")
    )
    result = graph.run(initial_message)
    """

    def __init__(self, name: str = "QAOpsPipeline"):
        self.name:          str                       = name
        self._nodes:        Dict[str, WorkflowNode]  = {}
        self._entry:        Optional[str]             = None
        self._state_mgr:    StateManager              = StateManager()

    # ------------------------------------------------------------------
    # Builder API  (fluent — every method returns self)
    # ------------------------------------------------------------------

    def add_node(
        self,
        name:    str,
        agent:   BaseAgent,
        skip_if: Optional[Callable[[Message], bool]] = None,
    ) -> "WorkflowGraph":
        """Register an agent as a named node."""
        if not isinstance(agent, BaseAgent):
            raise TypeError(
                f"Node '{name}': agent must be a BaseAgent subclass, "
                f"got {type(agent).__name__}"
            )
        self._nodes[name] = WorkflowNode(name=name, agent=agent, skip_if=skip_if)
        logger.debug(f"[WorkflowGraph] Node added: '{name}' ({agent.__class__.__name__})")
        return self

    def add_edge(
        self,
        from_node:  str,
        to_node:    str,
        condition:  Optional[Callable[[Message], bool]] = None,
        label:      str = "default",
    ) -> "WorkflowGraph":
        """Add a directed edge, optionally guarded by a condition function."""
        self._assert_node_exists(from_node)
        self._assert_node_exists(to_node)
        self._nodes[from_node].edges.append(
            Edge(target=to_node, condition=condition, label=label)
        )
        logger.debug(
            f"[WorkflowGraph] Edge: '{from_node}' → '{to_node}' "
            f"[{label}] condition={'yes' if condition else 'none'}"
        )
        return self

    def set_entry(self, name: str) -> "WorkflowGraph":
        """Set the entry node (first agent executed)."""
        self._assert_node_exists(name)
        self._entry = name
        return self

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self, message: Message) -> Message:
        """
        Execute the graph from the entry node.

        Returns the final Message produced by the last executed node.
        State is checkpointed after every node via StateManager.
        """
        if not self._entry:
            raise RuntimeError(
                "Entry node not set. Call set_entry() before run()."
            )
        if not isinstance(message, Message):
            message = Message.from_adk(message)

        with tracer.start_as_current_span(
            f"workflow.{self.name}",
            kind=trace.SpanKind.INTERNAL,
        ) as root_span:
            root_span.set_attribute("workflow.name",  self.name)
            root_span.set_attribute("workflow.entry", self._entry)
            root_span.set_attribute("msg.sender",     message.sender)

            pipeline_start = time.monotonic()
            exec_state     = self._state_mgr.new_execution(self.name)

            logger.info(
                f"[WorkflowGraph] START '{self.name}' "
                f"exec_id={exec_state.exec_id}"
            )

            try:
                result = self._traverse(
                    start_node=self._entry,
                    message=message,
                    exec_state=exec_state,
                    root_span=root_span,
                )

                duration_ms = (time.monotonic() - pipeline_start) * 1_000
                self._state_mgr.complete(exec_state)

                root_span.set_attribute("workflow.duration_ms", round(duration_ms, 2))
                root_span.set_attribute("workflow.nodes_run",   len(exec_state.visited))
                root_span.set_status(Status(StatusCode.OK))
                logger.info(
                    f"[WorkflowGraph] DONE '{self.name}' "
                    f"nodes={exec_state.visited} "
                    f"duration={duration_ms:.0f}ms"
                )
                return result

            except Exception as exc:
                self._state_mgr.fail(exec_state, str(exc))
                root_span.record_exception(exc)
                root_span.set_status(Status(StatusCode.ERROR, str(exc)))
                logger.error(f"[WorkflowGraph] FAILED: {exc}", exc_info=True)
                raise

    # ------------------------------------------------------------------
    # Traversal (recursive DFS — single path for sequential graphs)
    # ------------------------------------------------------------------

    def _traverse(
        self,
        start_node: str,
        message:    Message,
        exec_state: "ExecutionState",
        root_span:  trace.Span,
    ) -> Message:
        current_name    = start_node
        current_message = message

        while current_name:
            node = self._nodes[current_name]

            # --- Skip logic ---
            if node.skip_if and node.skip_if(current_message):
                logger.info(f"[WorkflowGraph] SKIP '{current_name}' (skip_if=True)")
                exec_state.visited.append(f"{current_name}[skipped]")
                current_name = self._next_node(node, current_message)
                continue

            # --- Execute node ---
            with tracer.start_as_current_span(
                f"node.{current_name}",
                kind=trace.SpanKind.INTERNAL,
            ) as node_span:
                node_span.set_attribute("node.name",  current_name)
                node_span.set_attribute("node.agent", node.agent.name)
                node_start = time.monotonic()

                current_message = node.agent.process(current_message)

                node_duration = (time.monotonic() - node_start) * 1_000
                node_span.set_attribute("node.duration_ms", round(node_duration, 2))

            exec_state.visited.append(current_name)
            self._state_mgr.checkpoint(exec_state, current_name, current_message)
            logger.debug(f"[WorkflowGraph] Checkpoint '{current_name}' saved")

            # --- Advance ---
            current_name = self._next_node(node, current_message)

        return current_message

    def _next_node(
        self, node: WorkflowNode, message: Message
    ) -> Optional[str]:
        """
        Evaluate outgoing edges and return the first passable target.
        Returns None if no edge is passable (terminal node).
        """
        for edge in node.edges:
            if edge.is_passable(message):
                logger.debug(
                    f"[WorkflowGraph] Edge '{node.name}' → '{edge.target}' "
                    f"[{edge.label}] ✓"
                )
                return edge.target
            else:
                logger.debug(
                    f"[WorkflowGraph] Edge '{node.name}' → '{edge.target}' "
                    f"[{edge.label}] ✗ condition blocked"
                )
        return None   # terminal

    # ------------------------------------------------------------------
    # Helpers & introspection
    # ------------------------------------------------------------------

    def _assert_node_exists(self, name: str) -> None:
        if name not in self._nodes:
            raise ValueError(
                f"Node '{name}' not found. "
                f"Registered nodes: {list(self._nodes.keys())}"
            )

    def describe(self) -> dict:
        """Return full graph topology — useful for logging and /health."""
        return {
            "name":  self.name,
            "entry": self._entry,
            "nodes": {
                n: {
                    "agent":   node.agent.describe(),
                    "edges":   [
                        {"target": e.target, "label": e.label,
                         "conditional": e.condition is not None}
                        for e in node.edges
                    ],
                    "skip_if": node.skip_if is not None,
                }
                for n, node in self._nodes.items()
            },
        }

    def __repr__(self) -> str:
        nodes = list(self._nodes.keys())
        return f"<WorkflowGraph name={self.name!r} nodes={nodes} entry={self._entry!r}>"