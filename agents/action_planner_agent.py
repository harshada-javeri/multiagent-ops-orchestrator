"""
ActionPlannerAgent — builds a remediation plan and raises a JIRA ticket.

Ticket creation via mcp-atlassian (Jira REST API) is triggered only when
the upstream RootCauseAnalyzerAgent reports confidence >= 0.8, ensuring
that low-quality analyses do not generate noise in the backlog.
"""
import os
import requests

from adk import Message
from agents.base_agent import BaseAgent

# ---------------------------------------------------------------------------
# Jira / mcp-atlassian configuration
# ---------------------------------------------------------------------------
_JIRA_URL      = os.getenv("JIRA_URL",      "https://cicdagent.atlassian.net")
_JIRA_PROJECT  = os.getenv("JIRA_PROJECT",  "SCRUM")

_CONFIDENCE_THRESHOLD = 0.8


def _jira_credentials() -> tuple[str, str]:
    """Return (username, api_token) supporting both naming conventions."""
    username = os.getenv("JIRA_USERNAME", "") or os.getenv("JIRA_USER", "")
    token    = os.getenv("JIRA_API_TOKEN", "") or os.getenv("JIRA_TOKEN", "")
    return username, token


class ActionPlannerAgent(BaseAgent):
    """Generates remediation steps and creates a JIRA ticket via mcp-atlassian."""

    def __init__(self, name: str = "ActionPlannerAgent", **kwargs):
        super().__init__(name=name, version="1.2.0", **kwargs)

    # ------------------------------------------------------------------
    # Internal helper — Jira REST API call (mcp-atlassian)
    # ------------------------------------------------------------------
    def _create_jira_ticket(
        self,
        summary: str,
        description: str,
        priority: str,
        error_categories: list,
        root_causes: list,
        confidence: float,
        plan: list,
    ) -> str:
        """
        Create a Jira issue using the Atlassian REST API and return its
        browse URL.  Returns an empty string on failure so the pipeline
        continues uninterrupted.
        """
        _JIRA_USERNAME, _JIRA_API_TOKEN = _jira_credentials()

        if not all([_JIRA_URL, _JIRA_USERNAME, _JIRA_API_TOKEN]):
            self._logger.warning(
                "[ActionPlannerAgent] Jira credentials not configured — skipping ticket creation."
            )
            return ""

        # Build a structured description from LLM analysis
        remediation_steps = "\n".join(f"# {step}" for step in plan)
        causes_text = "\n".join(f"* {c}" for c in root_causes)
        categories_text = ", ".join(error_categories)

        jira_description = (
            f"h2. Root Cause Analysis\n\n"
            f"*Identified Root Causes:*\n{causes_text}\n\n"
            f"*Error Categories:* {categories_text}\n\n"
            f"*AI Confidence Score:* {confidence:.0%}\n\n"
            f"----\n\n"
            f"h2. LLM Analysis\n\n"
            f"{description}\n\n"
            f"----\n\n"
            f"h2. Remediation Plan\n\n"
            f"{remediation_steps}\n\n"
            f"----\n\n"
            f"_Generated automatically by ActionPlannerAgent (confidence >= {_CONFIDENCE_THRESHOLD:.0%})_"
        )

        payload = {
            "fields": {
                "project":     {"key": _JIRA_PROJECT},
                "summary":     summary,
                "description": jira_description,
                "issuetype":   {"name": "Task"},
                "priority":    {"name": priority.capitalize()},
                "labels":      ["remediation", "cicd", "automated"] + [
                    c.replace(" ", "-") for c in error_categories
                ],
            }
        }

        try:
            resp = requests.post(
                f"{_JIRA_URL}/rest/api/2/issue",
                json=payload,
                auth=(_JIRA_USERNAME, _JIRA_API_TOKEN),
                timeout=15,
            )
            resp.raise_for_status()
            issue_key = resp.json().get("key", "")
            ticket_url = f"{_JIRA_URL}/browse/{issue_key}"
            self._logger.info(
                f"[ActionPlannerAgent] Jira ticket created via mcp-atlassian: {ticket_url}"
            )
            return ticket_url
        except requests.HTTPError as exc:
            self._logger.error(
                f"[ActionPlannerAgent] Jira API error {exc.response.status_code}: "
                f"{exc.response.text[:200]}"
            )
        except Exception as exc:
            self._logger.error(f"[ActionPlannerAgent] Jira ticket creation failed: {exc}")

        return ""

    # ------------------------------------------------------------------
    # Main agent logic
    # ------------------------------------------------------------------
    def _run(self, message: Message) -> Message:
        analysis: dict = message.content
        root_causes: list     = analysis.get("root_causes", [])
        confidence: float     = analysis.get("confidence", 0.0)
        error_categories: list = analysis.get("error_categories", [])
        llm_analysis: str     = analysis.get("analysis", "No LLM analysis available.")

        priority: str = "HIGH" if confidence >= _CONFIDENCE_THRESHOLD else "MEDIUM"

        # Build remediation plan only when confidence meets the threshold
        if confidence >= _CONFIDENCE_THRESHOLD:
            plan: list[str] = [
                f"Action {i + 1}: Investigate and fix '{cause}'"
                for i, cause in enumerate(root_causes)
            ] or ["Action 1: Review CI logs and rerun the failing tests"]

            # Raise a Jira ticket via mcp-atlassian
            ticket_url = self._create_jira_ticket(
                summary=f"QA Failure: {', '.join(root_causes[:2])}",
                description=llm_analysis,
                priority=priority,
                error_categories=error_categories,
                root_causes=root_causes,
                confidence=confidence,
                plan=plan,
            )
        else:
            plan = [
                "Confidence below threshold — manual review required before creating a remediation plan."
            ]
            ticket_url = ""
            self._logger.info(
                f"[{self.name}] Confidence {confidence:.2f} < {_CONFIDENCE_THRESHOLD} "
                "— skipping remediation plan and Jira ticket creation."
            )

        self._logger.info(
            f"[{self.name}] Plan ready | confidence={confidence:.2f} | "
            f"priority={priority} | ticket={ticket_url or 'N/A'}"
        )

        return Message(
            sender=self.name,
            receiver="Output",
            content={
                "plan":             plan,
                "ticket_url":       ticket_url,
                "ticket":           ticket_url,   # backward-compat alias
                "priority":         priority,
                "confidence":       confidence,
                "error_categories": error_categories,
            },
        )