"""
Unit tests for WorkflowGraph orchestrator.
Uses lightweight stub agents — no LLM or external tool calls.
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from adk import Message
from agents.base_agent import BaseAgent
from orchestration.workflow_graph import WorkflowGraph


class _EchoAgent(BaseAgent):
    """Stub agent that appends its name to the message content."""

    def __init__(self, name: str):
        super().__init__(name=name, version="0.0.0")

    def _run(self, message: Message) -> Message:
        content = message.content if isinstance(message.content, dict) else {}
        content[f"visited_{self.name}"] = True
        return Message(sender=self.name, receiver="next", content=content)

    def process(self, message: Message) -> Message:
        return self._run(message)


def _build_simple_graph() -> WorkflowGraph:
    return (
        WorkflowGraph()
        .add_node("a", _EchoAgent("a"))
        .add_node("b", _EchoAgent("b"))
        .add_node("c", _EchoAgent("c"))
        .add_edge("a", "b")
        .add_edge("b", "c")
        .set_entry("a")
    )


def test_graph_runs_all_nodes():
    graph = _build_simple_graph()
    result = graph.run(Message(sender="Test", receiver="a", content={}))
    assert result.content.get("visited_a")
    assert result.content.get("visited_b")
    assert result.content.get("visited_c")


def test_graph_describe_returns_topology():
    graph = _build_simple_graph()
    desc = graph.describe()
    assert desc["entry"] == "a"
    assert set(desc["nodes"].keys()) == {"a", "b", "c"}
    assert any(e["target"] == "b" for e in desc["nodes"]["a"]["edges"])


def test_graph_raises_without_entry():
    graph = WorkflowGraph().add_node("x", _EchoAgent("x"))
    with pytest.raises(RuntimeError, match="Entry node not set"):
        graph.run(Message(sender="T", receiver="x", content={}))


def test_conditional_edge_halts_graph():
    """A condition that returns False should stop traversal after node 'a'."""
    graph = (
        WorkflowGraph()
        .add_node("a", _EchoAgent("a"))
        .add_node("b", _EchoAgent("b"))
        .add_edge("a", "b", condition=lambda _msg: False)
        .set_entry("a")
    )
    result = graph.run(Message(sender="Test", receiver="a", content={}))
    assert result.content.get("visited_a")
    assert not result.content.get("visited_b")