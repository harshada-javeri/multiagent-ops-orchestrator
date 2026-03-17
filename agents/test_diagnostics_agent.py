"""
TestDiagnosticsAgent — parses raw CI log strings and extracts
failed test names, error categories, and a plain-text summary.
"""
import re
from adk import Message
from agents.base_agent import BaseAgent


class TestDiagnosticsAgent(BaseAgent):
    """Parses CI logs; extracts failed tests and error categories."""

    def __init__(self, name: str = "TestDiagnosticsAgent", **kwargs):
        super().__init__(name=name, version="1.1.0", **kwargs)

    def _run(self, message: Message) -> Message:
        if isinstance(message.content, str):
            logs: str = message.content
        elif isinstance(message.content, dict):
            logs = message.content.get("logs", str(message.content))
        else:
            logs = str(message.content)

        # ── Extract failed test names (multi-format) ─────────────────────
        # Format 1: "test_name FAILED"  (pytest / generic CI)
        pattern1 = re.findall(r"(\w+)\s+FAILED", logs)
        # Format 2: "Test failed: com.example.pkg.ClassName.methodName"  (JUnit/TestNG/Jenkins)
        pattern2 = re.findall(r"[Tt]est\s+failed:\s+[\w.]+\.(\w+)", logs)
        # Format 3: "FAILED tests/test_foo.py::TestClass::method_name"  (pytest verbose)
        pattern3 = re.findall(r"FAILED\s+\S+::(\w+)", logs)
        # Format 4: "FAILURE in testMethodName"  (some Jenkins reporters)
        pattern4 = re.findall(r"FAILURE\s+in\s+(\w+)", logs)

        failed_tests: list[str] = list(dict.fromkeys(pattern1 + pattern2 + pattern3 + pattern4))

        # ── Categorise error types ────────────────────────────────────────
        error_categories: list[str] = []
        if re.search(r"[Tt]imeout|TimeoutError", logs):
            error_categories.append("timeout")
        if re.search(r"[Aa]ssertion[Ee]rror|AssertionError|assert.*failed", logs, re.I):
            error_categories.append("assertion")
        if re.search(r"[Rr]ace[_\s][Cc]ondition|flaky", logs, re.I):
            error_categories.append("race_condition")
        if re.search(r"[Cc]onnection[Ee]rror|[Cc]onnection\s+refused|ConnectException", logs):
            error_categories.append("connection_error")
        if re.search(r"NullPointerException|NullReference|null pointer", logs, re.I):
            error_categories.append("null_pointer")
        if re.search(r"OutOfMemory|OOMError|heap space", logs, re.I):
            error_categories.append("out_of_memory")

        summary = (
            f"{len(failed_tests)} test(s) failed: {', '.join(failed_tests)}"
            if failed_tests
            else "No test failures detected"
        )

        self._logger.info(f"[{self.name}] {summary}")

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