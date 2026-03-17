"""
GitHubTool — fetches GitHub Actions workflow logs and creates GitHub Issues.

Used as a demo alternative when Jenkins/JIRA are not configured.
Requires: GITHUB_TOKEN, GITHUB_REPO environment variables.
"""
from __future__ import annotations

import os
import zipfile
import io
from typing import Optional

import requests

from tools.base_tool import BaseTool


class GitHubTool(BaseTool):
    """
    Wraps the GitHub REST API for:
      - Fetching Actions workflow run logs
      - Listing recent workflow runs
      - Creating GitHub Issues for CI failures
    """

    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        token: str = "",
        repo: str = "",
    ) -> None:
        super().__init__(name="GitHubTool")
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.repo  = repo  or os.getenv("GITHUB_REPO",  "")

        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self._headers["Authorization"] = f"Bearer {self.token}"

    # ------------------------------------------------------------------
    # BaseTool interface
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """Return True if GitHub API is reachable and token is valid."""
        try:
            resp = requests.get(
                f"{self.BASE_URL}/user",
                headers=self._headers,
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Workflow runs
    # ------------------------------------------------------------------

    def get_workflow_runs(
        self,
        repo: str = "",
        workflow: str = "",
        limit: int = 5,
    ) -> list[dict]:
        """
        List recent workflow runs for a repo.

        Args:
            repo:     "owner/repo" — falls back to GITHUB_REPO env var.
            workflow: Workflow file name (e.g. "ci.yml"). Omit for all.
            limit:    Maximum number of runs to return.

        Returns:
            List of run dicts from the GitHub API.
        """
        target_repo = repo or self.repo
        if not target_repo:
            self.logger.warning("[GitHubTool] GITHUB_REPO not set")
            return []

        if workflow:
            url = f"{self.BASE_URL}/repos/{target_repo}/actions/workflows/{workflow}/runs"
        else:
            url = f"{self.BASE_URL}/repos/{target_repo}/actions/runs"

        try:
            resp = requests.get(
                url,
                headers=self._headers,
                params={"per_page": limit},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("workflow_runs", [])
        except Exception as exc:
            self.logger.error(f"[GitHubTool] Failed to list runs: {exc}")
            return []

    def get_latest_workflow_logs(
        self,
        repo: str = "",
        workflow: str = "",
    ) -> str:
        """
        Fetch the console logs for the most recent workflow run.

        GitHub returns logs as a ZIP archive. This method extracts
        all .txt log files and concatenates them into a single string.

        Args:
            repo:     "owner/repo" — falls back to GITHUB_REPO env var.
            workflow: Workflow file name (e.g. "ci.yml"). Omit for latest run.

        Returns:
            Raw log text string, or a mock log if unavailable.
        """
        with self.tracer.start_as_current_span("github.get_latest_workflow_logs"):
            target_repo = repo or self.repo
            if not target_repo:
                self.logger.warning("[GitHubTool] GITHUB_REPO not set — returning mock logs")
                return self._mock_logs()

            runs = self.get_workflow_runs(repo=target_repo, workflow=workflow, limit=1)
            if not runs:
                self.logger.warning("[GitHubTool] No workflow runs found — returning mock logs")
                return self._mock_logs()

            run_id = runs[0]["id"]
            run_status = runs[0].get("conclusion", "unknown")
            self.logger.info(
                f"[GitHubTool] Latest run: id={run_id} status={run_status}"
            )

            # Download log archive
            log_url = (
                f"{self.BASE_URL}/repos/{target_repo}/actions/runs/{run_id}/logs"
            )
            try:
                resp = requests.get(
                    log_url,
                    headers=self._headers,
                    timeout=30,
                    allow_redirects=True,
                )
                resp.raise_for_status()
                return self._extract_logs_from_zip(resp.content)
            except Exception as exc:
                self.logger.error(f"[GitHubTool] Log download failed: {exc}")
                return self._mock_logs()

    def _extract_logs_from_zip(self, zip_bytes: bytes) -> str:
        """
        Extract all *.txt log files from a GitHub log ZIP archive
        and return them as a single concatenated string.
        """
        collected: list[str] = []
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                for name in sorted(zf.namelist()):
                    if name.endswith(".txt"):
                        with zf.open(name) as f:
                            text = f.read().decode("utf-8", errors="replace")
                            collected.append(f"=== {name} ===\n{text}")
        except Exception as exc:
            self.logger.error(f"[GitHubTool] ZIP extraction failed: {exc}")
            return self._mock_logs()

        return "\n".join(collected) if collected else self._mock_logs()

    # ------------------------------------------------------------------
    # GitHub Issues
    # ------------------------------------------------------------------

    def create_issue(
        self,
        title: str,
        body: str,
        repo: str = "",
        labels: Optional[list[str]] = None,
    ) -> str:
        """
        Create a GitHub Issue for a CI failure.

        Args:
            title:  Issue title (e.g. "CI Failure: test_login FAILED").
            body:   Markdown body — root-cause analysis + remediation plan.
            repo:   "owner/repo" — falls back to GITHUB_REPO env var.
            labels: Optional label list (e.g. ["bug", "ci-failure"]).

        Returns:
            HTML URL of the created issue, or a mock URL on failure.
        """
        with self.tracer.start_as_current_span("github.create_issue"):
            target_repo = repo or self.repo
            if not target_repo or not self.token:
                self.logger.warning(
                    "[GitHubTool] GITHUB_REPO or GITHUB_TOKEN not set "
                    "— returning mock issue URL"
                )
                return "https://github.com/mock-org/mock-repo/issues/0"

            payload: dict = {"title": title, "body": body}
            if labels:
                payload["labels"] = labels

            url = f"{self.BASE_URL}/repos/{target_repo}/issues"
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers=self._headers,
                    timeout=15,
                )
                resp.raise_for_status()
                issue_url: str = resp.json().get("html_url", "")
                self.logger.info(f"[GitHubTool] Issue created: {issue_url}")
                return issue_url
            except Exception as exc:
                self.logger.error(f"[GitHubTool] Issue creation failed: {exc}")
                return "https://github.com/mock-org/mock-repo/issues/ERR"

    # ------------------------------------------------------------------
    # Mock fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _mock_logs() -> str:
        return (
            "=== 1_Set up job.txt ===\n"
            "[INFO] Initializing GitHub Actions runner...\n"
            "=== 2_Run tests.txt ===\n"
            "[ERROR] test_login FAILED\n"
            "  AssertionError: Expected 200, got 500\n"
            "  at tests/test_auth.py:42\n"
            "[ERROR] test_checkout FAILED\n"
            "  TimeoutError: DB connection timeout after 30s\n"
            "  at tests/test_checkout.py:87\n"
            "=== 3_Post job.txt ===\n"
            "[INFO] Job failed. 2 tests failed.\n"
        )