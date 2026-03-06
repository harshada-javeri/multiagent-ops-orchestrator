"""
Unit tests for WorkflowGraph orchestrator.
Uses lightweight stub agents — no LLM or external tool calls.
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from adk import Message
from orchestration.workflow_graph import WorkflowGraph


class _EchoAgent:
    """Stub agent that appends its name to the message content."""

    def __init__(self, name: str):
        self.name = name

    def process(self, message: Message) -> Message:
        content = message.content if isinstance(message.content, dict) else {}
        content[f"visited_{self.name}"] = True
        return Message(sender=self.name, receiver="next", content=content)

    def describe(self):
        return {"name": self.name, "type": "_EchoAgent"}


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
    assert desc["nodes"]["a"]["next"] == ["b"]


def test_graph_raises_without_entry():
    graph = WorkflowGraph().add_node("x", _EchoAgent("x"))
    with pytest.raises(RuntimeError, match="No entry node"):
        graph.run(Message(sender="T", receiver="x", content={}))


def test_conditional_edge_halts_graph():
    """A condition that returns False should stop traversal after node 'a'."""
    graph = (
        WorkflowGraph()
        .add_node("a", _EchoAgent("a"))
        .add_node("b", _EchoAgent("b"), condition=lambda _msg: False)
        .add_edge("a", "b")
        .set_entry("a")
    )
    result = graph.run(Message(sender="Test", receiver="a", content={}))
    assert result.content.get("visited_a")
    assert not result.content.get("visited_b")