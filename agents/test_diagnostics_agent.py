"""
TestDiagnosticsAgent — parses raw CI log strings and extracts
failed test names, error categories, and a plain-text summary.
"""
import re
from adk import Message
from agents.base_agent import BaseAgent


class TestDiagnosticsAgent(BaseAgent):
    """Parses CI logs; extracts failed tests and error categories."""

    def __init__(self, name: str = "TestDiagnosticsAgent"):
        super().__init__(name=name, version="1.1.0")

    def _run(self, message: Message) -> Message:
        logs: str = (
            message.content
            if isinstance(message.content, str)
            else str(message.content)
        )

        # Extract failed test names
        failed_tests: list[str] = re.findall(r"(\w+)\s+FAILED", logs)

        # Categorise error types
        error_categories: list[str] = []
        if re.search(r"[Tt]imeout", logs):
            error_categories.append("timeout")
        if re.search(r"[Aa]ssertion[Ee]rror", logs):
            error_categories.append("assertion")
        if re.search(r"[Rr]ace[_\s][Cc]ondition|flaky", logs, re.I):
            error_categories.append("race_condition")
        if re.search(r"[Cc]onnection[Ee]rror|[Cc]onnection refused", logs):
            error_categories.append("connection_error")

        summary = (
            f"{len(failed_tests)} test(s) failed: {', '.join(failed_tests)}"
            if failed_tests
            else "No test failures detected"
        )

        self.logger.info(f"[{self.name}] {summary}")

        return Message(
            sender=self.name,
            receiver="RootCauseAnalyzerAgent",
            content={
                "failed_tests": failed_tests,
                "error_categories": error_categories,
                "summary": summary,
                "raw_logs": logs,
            },
        )