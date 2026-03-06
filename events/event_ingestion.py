"""
EventIngestionLayer — validates, normalises, and dispatches
inbound CI failure events.

Acts as the front door for all triggers (webhook, CLI, API).
Handlers are registered at startup and called for every event.
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
        logger.info(f"[EventIngestion] Handler registered: {handler.__class__.__name__}")

    def ingest(self, raw: Dict[str, Any]) -> CIFailureEvent:
        """
        Validate a raw dict payload and dispatch to all handlers.

        Args:
            raw: Unvalidated dict (from Flask JSON body, CLI arg, etc.)

        Returns:
            Validated CIFailureEvent.

        Raises:
            pydantic.ValidationError: If required fields are missing.
        """
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

    def ingest_logs(
        self,
        ci_logs: str,
        source: str = "manual",
        **kwargs: Any,
    ) -> CIFailureEvent:
        """Convenience wrapper for raw log strings (used by CLI / orchestrator)."""
        return self.ingest({"ci_logs": ci_logs, "source": source, **kwargs})