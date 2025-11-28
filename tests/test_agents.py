import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.test_diagnostics_agent import TestDiagnosticsAgent
from agents.root_cause_agent import RootCauseAnalyzerAgent
from agents.action_planner_agent import ActionPlannerAgent


def test_test_diagnostics_agent():
    agent = TestDiagnosticsAgent(name="TestDiagnostics")
    logs = "[ERROR] test_login FAILED\n[INFO] Build finished"
    result = agent.process(logs)
    assert "failed_tests" in result


def test_root_cause_agent():
    agent = RootCauseAnalyzerAgent(name="RootCause")
    diag_result = {"failed_tests": ["test_login FAILED"]}
    result = agent.process(diag_result)
    assert "summary" in result


def test_action_planner_agent():
    agent = ActionPlannerAgent(name="ActionPlanner")
    rca_result = {"summary": "Login test is flaky"}
    result = agent.process(rca_result)
    assert "plan" in result
