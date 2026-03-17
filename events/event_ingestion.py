"""
EventIngestionLayer — validates, normalises, and dispatches
inbound CI failure events.

Supports GitHub Actions payloads:
  {
      "source":   "github_actions",
      "repo":     "owner/repo",        ← auto-fetches logs if no ci_logs
      "workflow": "ci.yml",
      "ci_logs":  "..."                ← optional; fetched live if absent
  }
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List

from events.event_schema import CIFailureEvent
from utils.logger import get_logger

logger = get_logger("EventIngestionLayer")


class EventIngestionLayer:
    """Validates raw payloads and fans out to registered handlers."""

    def __init__(self) -> None:
        self._handlers: List[Callable[[CIFailureEvent], Any]] = []

    def register_handler(self, handler: Callable[[CIFailureEvent], Any]) -> None:
        """Register a downstream handler (e.g. EventRouter.__call__)."""
        self._handlers.append(handler)
        logger.info(
            f"[EventIngestion] Handler registered: {handler.__class__.__name__}"
        )

    # ------------------------------------------------------------------
    # Primary ingestion entry point
    # ------------------------------------------------------------------

    def ingest(self, raw: Dict[str, Any]) -> CIFailureEvent:
        """
        Validate a raw dict payload and dispatch to all handlers.

        Special handling for GitHub Actions events:
          - If source == "github_actions" and ci_logs is absent,
            automatically fetches the latest workflow run logs via GitHubTool.
          - "repo" and "workflow" fields are moved into metadata.

        Args:
            raw: Unvalidated dict (from Flask JSON body, CLI arg, etc.)

        Returns:
            Validated CIFailureEvent.

        Raises:
            pydantic.ValidationError: If required fields are missing after enrichment.
        """
        raw = dict(raw)  # shallow copy — do not mutate caller's dict

        source = raw.get("source", "manual")

        if source == "github_actions":
            raw = self._enrich_github_event(raw)

        event = CIFailureEvent(**raw)
        logger.info(
            f"[EventIngestion] event_id={event.event_id} "
            f"source={event.source} severity={event.severity}"
        )

        for handler in self._handlers:
            try:
                handler(event)
            except Exception as exc:
                logger.error(
                    f"[EventIngestion] Handler {handler.__class__.__name__} "
                    f"raised: {exc}",
                    exc_info=True,
                )

        return event

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------

    def ingest_logs(
        self,
        ci_logs: str,
        source: str = "manual",
        **kwargs: Any,
    ) -> CIFailureEvent:
        """Convenience wrapper for raw log strings (used by CLI / orchestrator)."""
        return self.ingest({"ci_logs": ci_logs, "source": source, **kwargs})

    def ingest_github_event(
        self,
        repo: str = "",
        workflow: str = "",
        ci_logs: str = "",
        **kwargs: Any,
    ) -> CIFailureEvent:
        """
        Convenience wrapper for GitHub Actions events.

        If ci_logs is empty the GitHubTool will fetch them automatically.

        Args:
            repo:     "owner/repo" — falls back to GITHUB_REPO env var.
            workflow: Workflow file name — e.g. "ci.yml".
            ci_logs:  Pre-fetched log text (optional).
        """
        payload: Dict[str, Any] = {
            "source": "github_actions",
            "repo":     repo,
            "workflow": workflow,
            **kwargs,
        }
        if ci_logs:
            payload["ci_logs"] = ci_logs
        return self.ingest(payload)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _enrich_github_event(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        If a GitHub Actions payload has no ci_logs, fetch them live
        using GitHubTool. Moves repo/workflow into metadata.
        """
        repo     = raw.pop("repo", "")
        workflow = raw.pop("workflow", "")

        # Preserve repo/workflow in metadata for downstream consumers
        meta = raw.setdefault("metadata", {})
        if repo:
            meta["github_repo"] = repo
        if workflow:
            meta["github_workflow"] = workflow

        if not raw.get("ci_logs"):
            logger.info(
                f"[EventIngestion] GitHub source — fetching logs for "
                f"repo='{repo}' workflow='{workflow}'"
            )
            raw["ci_logs"] = self._fetch_github_logs(repo=repo, workflow=workflow)

        return raw

    @staticmethod
    def _fetch_github_logs(repo: str, workflow: str) -> str:
        """
        Delegate log fetching to GitHubTool via ToolRegistry.
        Falls back gracefully if the tool is not registered.
        """
        try:
            from tools.tool_registry import ToolRegistry
            github = ToolRegistry.get("github")
            if github:
                return github.get_latest_workflow_logs(repo=repo, workflow=workflow)
        except Exception as exc:
            logger.error(f"[EventIngestion] GitHub log fetch failed: {exc}")

        return "[ERROR] test_ci FAILED\nCould not fetch GitHub Actions logs."