"""JiraTool — creates JIRA issues for detected CI failures."""
import os
import requests
from tools.base_tool import BaseTool


class JiraTool(BaseTool):
    """Wraps the JIRA REST API for ticket creation."""

    def __init__(
        self,
        url: str = "",
        user: str = "",
        token: str = "",
    ) -> None:
        super().__init__(name="JiraTool")
        self.url   = url   or os.getenv("JIRA_URL",   "")
        self.user  = user  or os.getenv("JIRA_USER",  "")
        self.token = token or os.getenv("JIRA_TOKEN", "")

    def health_check(self) -> bool:
        try:
            resp = requests.get(
                f"{self.url}/rest/api/2/myself",
                auth=(self.user, self.token),
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def create_ticket(
        self,
        summary: str,
        description: str,
        priority: str = "HIGH",
    ) -> str:
        """
        Create a JIRA issue and return its URL.
        Falls back gracefully when JIRA is unreachable.
        """
        with self.tracer.start_as_current_span("jira.create_ticket"):
            if not all([self.url, self.user, self.token]):
                self.logger.warning("[JiraTool] JIRA not configured — returning mock URL")
                return f"https://mock-jira.local/browse/QA-0001"
            payload = {
                "fields": {
                    "project": {"key": os.getenv("JIRA_PROJECT", "QA")},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": "Bug"},
                    "priority": {"name": priority.capitalize()},
                }
            }
            try:
                resp = requests.post(
                    f"{self.url}/rest/api/2/issue",
                    json=payload,
                    auth=(self.user, self.token),
                    timeout=15,
                )
                resp.raise_for_status()
                key = resp.json().get("key", "QA-???")
                return f"{self.url}/browse/{key}"
            except Exception as exc:
                self.logger.error(f"[JiraTool] Ticket creation failed: {exc}")
                return f"https://mock-jira.local/browse/QA-ERR"


# ---------------------------------------------------------------------------
# Module-level helper — backward compatibility
# ---------------------------------------------------------------------------
def create_jira_ticket(summary: str, description: str) -> str:
    return JiraTool().create_ticket(summary=summary, description=description)