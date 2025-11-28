import sys
import os
import pytest
from tools.jenkins_tool import JenkinsTool
from tools.jira_tool import JiraTool
from tools.grafana_tool import GrafanaTool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_jenkins_tool():
    tool = JenkinsTool()
    logs = tool.fetch_ci_logs()
    assert isinstance(logs, str)


def test_jira_tool():
    tool = JiraTool()
    ticket = tool.create_ticket("Test failure", "Details...")
    assert "JIRA" in ticket


def test_grafana_tool():
    tool = GrafanaTool()
    metrics = tool.fetch_metrics()
    assert isinstance(metrics, dict)
