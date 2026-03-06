"""
ActionPlannerAgent — builds a remediation plan and raises a JIRA ticket.
"""
from adk import Message
from agents.base_agent import BaseAgent


class ActionPlannerAgent(BaseAgent):
    """Generates remediation steps and creates a JIRA ticket."""

    def __init__(self, name: str = "ActionPlannerAgent"):
        super().__init__(name=name, version="1.1.0")

    def _run(self, message: Message) -> Message:
        # Import here to avoid circular import at module load time
        from tools.tool_registry import ToolRegistry

        analysis: dict = message.content
        root_causes: list = analysis.get("root_causes", [])
        confidence: float = analysis.get("confidence", 0.0)
        error_categories: list = analysis.get("error_categories", [])

        priority: str = "HIGH" if confidence >= 0.8 else "MEDIUM"

        plan: list[str] = [
            f"Action {i + 1}: Investigate and fix '{cause}'"
            for i, cause in enumerate(root_causes)
        ] or ["Action 1: Review CI logs and rerun the failing tests"]

        # Create JIRA ticket via registry (safe if tool is absent)
        ticket_url: str = ""
        jira = ToolRegistry.get("jira")
        if jira:
            try:
                ticket_url = jira.create_ticket(
                    summary=f"QA Failure: {', '.join(root_causes[:2])}",
                    description=analysis.get("analysis", ""),
                    priority=priority,
                )
            except Exception as exc:
                self.logger.warning(f"JIRA ticket creation failed: {exc}")

        self.logger.info(
            f"[{self.name}] Plan ready | priority={priority} | ticket={ticket_url}"
        )

        return Message(
            sender=self.name,
            receiver="Output",
            content={
                "plan": plan,
                "ticket_url": ticket_url,
                "ticket": ticket_url,         # backward-compat alias
                "priority": priority,
                "confidence": confidence,
                "error_categories": error_categories,
            },
        )