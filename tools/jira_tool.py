from utils.logger import get_logger

class JiraTool:
    """
    Tool for creating JIRA tickets.
    """
    def create_ticket(self, summary: str, description: str) -> str:
        logger = get_logger("JiraTool")
        logger.info(f"Creating JIRA ticket: {summary}")
        return f"JIRA ticket created: {summary}"
# tools/jira_tool.py
def create_jira_ticket(summary: str, description: str) -> str:
    logger = get_logger("JiraTool")
    logger.info(f"Creating mock JIRA ticket: {summary}")
    return f"https://mock-jira.local/ticket/QA-{hash(summary) % 1000}"
# End of tools/jira_tool.py