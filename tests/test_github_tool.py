"""
Unit tests for GitHubTool and GitHub Actions event ingestion.
No live network calls — all external requests are mocked.
"""
from __future__ import annotations

import io
import sys
import os
import zipfile
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.github_tool import GitHubTool
from events.event_ingestion import EventIngestionLayer
from events.event_schema import CIFailureEvent


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_zip(files: dict[str, str]) -> bytes:
    """Build an in-memory ZIP archive from {filename: content} dict."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


# ── GitHubTool unit tests ─────────────────────────────────────────────────

def test_github_tool_describe():
    tool = GitHubTool()
    desc = tool.describe()
    assert desc["name"] == "GitHubTool"
    assert desc["type"] == "GitHubTool"


def test_github_tool_mock_logs_returned_when_no_repo():
    tool = GitHubTool(token="", repo="")
    logs = tool.get_latest_workflow_logs()
    assert "FAILED" in logs
    assert isinstance(logs, str)


def test_github_tool_mock_issue_url_when_not_configured():
    tool = GitHubTool(token="", repo="")
    url = tool.create_issue(title="Test failure", body="Details")
    assert "mock" in url.lower()
    assert "github.com" in url


@patch("requests.get")
def test_github_tool_get_workflow_runs(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "workflow_runs": [
                {"id": 42, "conclusion": "failure", "name": "CI"}
            ]
        },
    )
    mock_get.return_value.raise_for_status = lambda: None

    tool = GitHubTool(token="ghp_fake", repo="owner/repo")
    runs = tool.get_workflow_runs(repo="owner/repo")
    assert len(runs) == 1
    assert runs[0]["id"] == 42


@patch("requests.get")
def test_github_tool_get_latest_logs_extracts_zip(mock_get):
    zip_bytes = _make_zip({
        "1_Set up job.txt": "[INFO] Starting\n",
        "2_Run tests.txt": "[ERROR] test_login FAILED\n",
    })

    # First call → workflow runs list
    runs_resp = MagicMock(
        status_code=200,
        json=lambda: {"workflow_runs": [{"id": 99, "conclusion": "failure"}]},
    )
    runs_resp.raise_for_status = lambda: None

    # Second call → log ZIP
    logs_resp = MagicMock(status_code=200, content=zip_bytes)
    logs_resp.raise_for_status = lambda: None

    mock_get.side_effect = [runs_resp, logs_resp]

    tool = GitHubTool(token="ghp_fake", repo="owner/repo")
    logs = tool.get_latest_workflow_logs()
    assert "test_login FAILED" in logs
    assert "Set up job" in logs


@patch("requests.post")
def test_github_tool_create_issue_returns_url(mock_post):
    mock_post.return_value = MagicMock(
        status_code=201,
        json=lambda: {"html_url": "https://github.com/owner/repo/issues/7"},
    )
    mock_post.return_value.raise_for_status = lambda: None

    tool = GitHubTool(token="ghp_fake", repo="owner/repo")
    url = tool.create_issue(title="CI Failure", body="Details")
    assert url == "https://github.com/owner/repo/issues/7"


# ── EventIngestionLayer GitHub enrichment tests ───────────────────────────

def test_ingestion_github_event_uses_provided_logs():
    """When ci_logs is provided in a github_actions event, no fetch is attempted."""
    received: list[CIFailureEvent] = []

    ingress = EventIngestionLayer()
    ingress.register_handler(received.append)

    event = ingress.ingest({
        "source":   "github_actions",
        "repo":     "owner/repo",
        "workflow": "ci.yml",
        "ci_logs":  "[ERROR] test_api FAILED",
    })

    assert event.source == "github_actions"
    assert event.ci_logs == "[ERROR] test_api FAILED"
    assert event.metadata.get("github_repo") == "owner/repo"
    assert event.metadata.get("github_workflow") == "ci.yml"
    assert len(received) == 1


def test_ingestion_github_event_fetches_logs_when_absent():
    """When ci_logs is missing, GitHubTool.get_latest_workflow_logs is called."""
    ingress = EventIngestionLayer()

    fake_logs = "[ERROR] test_build FAILED\n  AssertionError"

    with patch(
        "events.event_ingestion.EventIngestionLayer._fetch_github_logs",
        return_value=fake_logs,
    ):
        event = ingress.ingest({
            "source":   "github_actions",
            "repo":     "owner/repo",
            "workflow": "build.yml",
        })

    assert "test_build FAILED" in event.ci_logs
    assert event.metadata.get("github_repo") == "owner/repo"


def test_ingestion_github_convenience_method():
    ingress = EventIngestionLayer()
    with patch(
        "events.event_ingestion.EventIngestionLayer._fetch_github_logs",
        return_value="[ERROR] test_x FAILED",
    ):
        event = ingress.ingest_github_event(repo="owner/repo", workflow="ci.yml")

    assert event.source == "github_actions"
    assert "test_x FAILED" in event.ci_logs