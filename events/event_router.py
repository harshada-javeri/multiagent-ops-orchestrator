"""
EventRouter — maps a validated CIFailureEvent to a WorkflowGraph run.

Bridges the ingestion layer and the orchestration layer.
"""
from adk import Message

from events.event_schema import CIFailureEvent
from orchestration.workflow_runner import build_qaops_graph
from utils.logger import get_logger
from utils.memory_handler import update_memory

logger = get_logger("EventRouter")


class EventRouter:
    """Routes CIFailureEvents through the QAOps WorkflowGraph."""

    def __init__(self, dry_run: bool = True) -> None:
        self.graph = build_qaops_graph(dry_run=dry_run)
        logger.info(f"[EventRouter] Graph: {self.graph.describe()}")

    def __call__(self, event: CIFailureEvent) -> dict:
        """Handle a single event end-to-end."""
        logger.info(f"[EventRouter] Routing event_id={event.event_id}")

        initial_message = Message(
            sender="EventRouter",
            receiver="diagnostics",
            content=event.ci_logs,
        )

        result = self.graph.run(initial_message)

        # Persist recurring failures to long-term memory
        for test in result.content.get("failed_tests", []):
            update_memory(test)

        return {
            "event_id": event.event_id,
            "source": event.source,
            **result.content,
        }