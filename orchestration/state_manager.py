"""
StateManager — execution state, checkpointing, and audit trail.

Responsibilities
----------------
- Allocate a unique ExecutionState per pipeline run
- Checkpoint Message content after each node completes
- Track timing, visited nodes, and failure info
- Persist state to memory_bank.json for post-run inspection
- Provide replay-ready snapshots (future use)

No external DB required — uses in-memory dict + optional JSON flush.
"""
from __future__ import annotations

import json
import uuid
import time
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents.base_agent import Message
from utils.logger import get_logger

logger = get_logger("StateManager")

# Where to persist execution history (alongside memory_bank.json)
_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "execution_state.json"
)


# ---------------------------------------------------------------------------
# ExecutionState
# ---------------------------------------------------------------------------

@dataclass
class NodeCheckpoint:
    """Snapshot of a Message after a specific node completes."""
    node:          str
    timestamp_utc: str
    message:       Dict[str, Any]    # Message.to_dict() snapshot


@dataclass
class ExecutionState:
    """
    Full runtime state for one pipeline execution.

    Created by StateManager.new_execution().
    Updated by StateManager.checkpoint() after each node.
    Closed by StateManager.complete() or StateManager.fail().
    """
    exec_id:       str                    = field(default_factory=lambda: str(uuid.uuid4())[:8])
    workflow_name: str                    = ""
    status:        str                    = "running"    # running | completed | failed
    visited:       List[str]              = field(default_factory=list)
    checkpoints:   List[NodeCheckpoint]   = field(default_factory=list)
    error:         Optional[str]          = None
    started_at:    float                  = field(default_factory=time.monotonic)
    finished_at:   Optional[float]        = None
    metadata:      Dict[str, Any]         = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        if self.finished_at:
            return round((self.finished_at - self.started_at) * 1_000, 2)
        return None

    def to_dict(self) -> dict:
        return {
            "exec_id":       self.exec_id,
            "workflow_name": self.workflow_name,
            "status":        self.status,
            "visited":       self.visited,
            "error":         self.error,
            "duration_ms":   self.duration_ms,
            "checkpoints":   [
                {
                    "node":          cp.node,
                    "timestamp_utc": cp.timestamp_utc,
                    "content_keys":  list(cp.message.get("content", {}).keys())
                                     if isinstance(cp.message.get("content"), dict)
                                     else ["raw"],
                }
                for cp in self.checkpoints
            ],
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# StateManager
# ---------------------------------------------------------------------------

class StateManager:
    """
    Manages ExecutionState lifecycle for WorkflowGraph runs.

    All state is held in-memory and optionally flushed to
    execution_state.json for persistence between process restarts.
    """

    def __init__(self, persist: bool = True):
        self._persist  = persist
        self._store:   Dict[str, ExecutionState] = {}   # exec_id → state
        self._history: List[dict]                = self._load_history()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def new_execution(self, workflow_name: str) -> ExecutionState:
        """Allocate and register a new ExecutionState."""
        state = ExecutionState(workflow_name=workflow_name)
        self._store[state.exec_id] = state
        logger.info(
            f"[StateManager] New execution: exec_id={state.exec_id} "
            f"workflow='{workflow_name}'"
        )
        return state

    def checkpoint(
        self,
        state:        ExecutionState,
        node_name:    str,
        message:      Message,
    ) -> None:
        """
        Save a Message snapshot after a node completes.
        Safe to call from within the graph traversal loop.
        """
        # Safely serialise — works with custom Message (has to_dict) and ADK Message
        if hasattr(message, "to_dict") and callable(message.to_dict):
            msg_dict = message.to_dict()
        else:
            msg_dict = {
                "sender":   getattr(message, "sender",   "unknown"),
                "receiver": getattr(message, "receiver", "unknown"),
                "content":  getattr(message, "content",  {}),
                "metadata": getattr(message, "metadata", {}),
            }
        cp = NodeCheckpoint(
            node=node_name,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            message=msg_dict,
        )
        state.checkpoints.append(cp)
        logger.debug(
            f"[StateManager] Checkpoint: exec_id={state.exec_id} "
            f"node='{node_name}'"
        )

    def complete(self, state: ExecutionState) -> None:
        """Mark execution as successfully completed."""
        state.status      = "completed"
        state.finished_at = time.monotonic()
        logger.info(
            f"[StateManager] Completed: exec_id={state.exec_id} "
            f"duration={state.duration_ms}ms nodes={state.visited}"
        )
        self._archive(state)

    def fail(self, state: ExecutionState, error: str) -> None:
        """Mark execution as failed with error message."""
        state.status      = "failed"
        state.error       = error
        state.finished_at = time.monotonic()
        logger.error(
            f"[StateManager] Failed: exec_id={state.exec_id} "
            f"error='{error}'"
        )
        self._archive(state)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, exec_id: str) -> Optional[ExecutionState]:
        """Retrieve live state by exec_id."""
        return self._store.get(exec_id)

    def latest(self) -> Optional[ExecutionState]:
        """Return the most recently created ExecutionState."""
        if not self._store:
            return None
        return list(self._store.values())[-1]

    def summary(self) -> dict:
        """Return counts and recent history — used by /health endpoint."""
        statuses = [s.status for s in self._store.values()]
        return {
            "total":     len(statuses),
            "completed": statuses.count("completed"),
            "failed":    statuses.count("failed"),
            "running":   statuses.count("running"),
            "recent":    self._history[-5:],   # last 5 archived runs
        }

    # ------------------------------------------------------------------
    # Replay helper (future async extension)
    # ------------------------------------------------------------------

    def get_checkpoint_message(
        self, exec_id: str, node_name: str
    ) -> Optional[Message]:
        """
        Reconstruct a Message from a previously saved checkpoint.
        Enables re-running the graph from any intermediate node.
        """
        state = self.get(exec_id)
        if not state:
            logger.warning(f"[StateManager] exec_id '{exec_id}' not found")
            return None

        for cp in state.checkpoints:
            if cp.node == node_name:
                d = cp.message
                return Message(
                    sender=d.get("sender",   "replay"),
                    receiver=d.get("receiver", "unknown"),
                    content=d.get("content",  {}),
                    metadata=d.get("metadata", {}),
                )
        return None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _archive(self, state: ExecutionState) -> None:
        """Append completed/failed run to history and optionally flush."""
        entry = state.to_dict()
        self._history.append(entry)
        # Keep only last 100 executions in memory
        if len(self._history) > 100:
            self._history = self._history[-100:]
        if self._persist:
            self._flush_history()

    def _flush_history(self) -> None:
        """Write execution history to disk."""
        try:
            with open(_STATE_FILE, "w") as fh:
                json.dump(
                    {"executions": self._history},
                    fh,
                    indent=2,
                    default=str,
                )
        except OSError as exc:
            logger.warning(f"[StateManager] Could not persist state: {exc}")

    def _load_history(self) -> list:
        """Load previous execution history from disk at startup."""
        if not os.path.exists(_STATE_FILE):
            return []
        try:
            with open(_STATE_FILE) as fh:
                data = json.load(fh)
                history = data.get("executions", [])
                logger.info(
                    f"[StateManager] Loaded {len(history)} historical executions"
                )
                return history
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning(f"[StateManager] Could not load history: {exc}")
            return []