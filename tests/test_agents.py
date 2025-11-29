import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.test_diagnostics_agent import TestDiagnosticsAgent
from agents.root_cause_agent import RootCauseAnalyzerAgent
from agents.action_planner_agent import ActionPlannerAgent
from adk import Message


def test_test_diagnostics_agent():
    agent = TestDiagnosticsAgent(name="TestDiagnostics")
    logs = "[ERROR] test_login FAILED\n[INFO] Build finished"
    message = Message(sender="Test", receiver="TestDiagnostics", content=logs)
    result = agent.process(message)
    assert "failed_tests" in result.content
    assert result.sender == "TestDiagnostics"


def test_root_cause_agent():
    agent = RootCauseAnalyzerAgent(name="RootCause")
    diag_result = {"failed_tests": ["test_login FAILED"]}
    message = Message(sender="TestDiagnostics", receiver="RootCause", content=diag_result)
    result = agent.process(message)
    assert "analysis" in result.content
    assert result.sender == "RootCause"


def test_action_planner_agent():
    agent = ActionPlannerAgent(name="ActionPlanner")
    rca_result = {"analysis": "Login test is flaky"}
    message = Message(sender="RootCause", receiver="ActionPlanner", content=rca_result)
    result = agent.process(message)
    assert "plan" in result.content
    assert result.sender == "ActionPlanner"
