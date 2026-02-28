# agents/action_planner_agent.py
from adk import Agent, Message
from tools.jira_tool import create_jira_ticket

from typing import Any

from utils.logger import get_logger

from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name="multiagent-orchestrator")
class ActionPlannerAgent(Agent):
    """
    Agent that proposes fixes or creates JIRA tickets based on root cause analysis.

    Methods
    -------
    process(message: Message) -> Message
        Proposes remediation and creates JIRA ticket.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.logger = get_logger(self.__class__.__name__)

    def process(self, message: Message) -> Message:
        analysis: Any = message.content["analysis"]
        remediation_plan: str = "Recommended Action: restart failing jobs, or fix test modules."
        ticket_url: str = create_jira_ticket(summary="QA Failure", description=analysis)
        self.logger.info(f"Remediation plan: {remediation_plan}, Ticket: {ticket_url}")
        return Message(
            sender=self.name,
            receiver="LoggerAgent",
            content={"plan": remediation_plan, "ticket": ticket_url}
        )
# End of agents/action_planner_agent.py