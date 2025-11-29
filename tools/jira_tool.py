# tools/jira_tool.py
from utils.logger import get_logger

class JiraTool:
    """
    Tool for creating JIRA tickets.
    """
    @staticmethod
    def create_ticket(summary: str, description: str) -> str:
        logger = get_logger("JiraTool")
        logger.info(f"Creating JIRA ticket: {summary}")
        return f"https://mock-jira.local/ticket/QA-{hash(summary) % 1000}"

def create_jira_ticket(summary: str, description: str) -> str:
    """Legacy function wrapper."""
    return JiraTool.create_ticket(summary, description)
# End of tools/jira_tool.py