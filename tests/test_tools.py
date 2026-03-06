import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.jenkins_tool import JenkinsTool
from tools.jira_tool import JiraTool
from tools.grafana_tool import GrafanaTool
from tools.tool_registry import ToolRegistry


def test_jenkins_tool_returns_string():
    tool = JenkinsTool()
    logs = tool.fetch_ci_logs()
    assert isinstance(logs, str)
    assert len(logs) > 0


def test_jira_tool_returns_url():
    tool = JiraTool()
    url = tool.create_ticket("Test failure", "Details of the failure")
    assert isinstance(url, str)
    assert "jira" in url.lower() or "mock" in url.lower()


def test_grafana_tool_returns_dict():
    tool = GrafanaTool()
    metrics = tool.fetch_metrics()
    assert isinstance(metrics, dict)
    assert len(metrics) > 0


def test_tool_registry_bootstrap_and_get():
    ToolRegistry.bootstrap()
    assert ToolRegistry.get("jenkins") is not None
    assert ToolRegistry.get("jira") is not None
    assert ToolRegistry.get("grafana") is not None


def test_tool_registry_missing_key_returns_none():
    result = ToolRegistry.get("nonexistent_tool_xyz")
    assert result is None


def test_tool_registry_list_tools():
    ToolRegistry.bootstrap()
    tools = ToolRegistry.list_tools()
    assert isinstance(tools, dict)
    assert "jenkins" in tools


def test_base_tool_describe():
    tool = JenkinsTool()
    desc = tool.describe()
    assert desc["name"] == "JenkinsTool"
    assert desc["type"] == "JenkinsTool"
