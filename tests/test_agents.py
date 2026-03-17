import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from adk import Message
from agents.test_diagnostics_agent import TestDiagnosticsAgent
from agents.root_cause_agent import RootCauseAnalyzerAgent
from agents.action_planner_agent import ActionPlannerAgent
from agents.execution_agent import ExecutionAgent
from agents.base_agent import BaseAgent


# ---------------------------------------------------------------------------
# BaseAgent interface
# ---------------------------------------------------------------------------

def test_base_agent_is_abstract():
    with pytest.raises(TypeError):
        BaseAgent(name="abstract")  # cannot instantiate directly


# ---------------------------------------------------------------------------
# TestDiagnosticsAgent
# ---------------------------------------------------------------------------

def test_test_diagnostics_agent_basic():
    agent = TestDiagnosticsAgent(name="TestDiagnostics")
    message = Message(
        sender="Test",
        receiver="TestDiagnostics",
        content="[ERROR] test_login FAILED\n[INFO] Build finished",
    )
    result = agent.process(message)
    assert "failed_tests" in result.content
    assert "test_login" in result.content["failed_tests"]
    assert result.sender == "TestDiagnostics"


def test_test_diagnostics_agent_no_failures():
    agent = TestDiagnosticsAgent()
    result = agent.process(
        Message(sender="T", receiver="D", content="[INFO] All tests passed")
    )
    assert result.content["failed_tests"] == []


def test_test_diagnostics_error_categorisation():
    agent = TestDiagnosticsAgent()
    result = agent.process(
        Message(
            sender="T",
            receiver="D",
            content="[ERROR] test_x FAILED\nTimeoutError: db timeout",
        )
    )
    assert "timeout" in result.content["error_categories"]


# ---------------------------------------------------------------------------
# RootCauseAnalyzerAgent
# ---------------------------------------------------------------------------

def test_root_cause_agent():
    agent = RootCauseAnalyzerAgent(name="RootCause")
    message = Message(
        sender="TestDiagnostics",
        receiver="RootCause",
        content={"failed_tests": ["test_login FAILED"], "error_categories": [], "raw_logs": ""},
    )
    result = agent.process(message)
    assert "analysis" in result.content
    assert result.sender == "RootCause"


# ---------------------------------------------------------------------------
# ActionPlannerAgent
# ---------------------------------------------------------------------------

def test_action_planner_agent():
    agent = ActionPlannerAgent(name="ActionPlanner")
    message = Message(
        sender="RootCause",
        receiver="ActionPlanner",
        content={
            "analysis": "Login test is flaky",
            "root_causes": ["test_login"],
            "confidence": 0.85,
            "error_categories": ["timeout"],
        },
    )
    result = agent.process(message)
    assert "plan" in result.content
    assert result.sender == "ActionPlanner"


# ---------------------------------------------------------------------------
# ExecutionAgent
# ---------------------------------------------------------------------------

def test_execution_agent_dry_run():
    agent = ExecutionAgent(dry_run=True)
    message = Message(
        sender="ActionPlanner",
        receiver="ExecutionAgent",
        content={
            "plan": ["Action 1: fix db index"],
            "confidence": 0.95,
            "priority": "HIGH",
        },
    )
    result = agent.process(message)
    assert result.content["auto_executed"] is False
    assert all(
        r["status"] == "pending_approval"
        for r in result.content["execution_results"]
    )


def test_execution_agent_low_confidence_no_auto_exec():
    """Even with dry_run=False, low confidence prevents auto-execution."""
    agent = ExecutionAgent(dry_run=False)
    message = Message(
        sender="AP",
        receiver="EA",
        content={"plan": ["fix something"], "confidence": 0.5, "priority": "LOW"},
    )
    result = agent.process(message)
    assert result.content["auto_executed"] is False
