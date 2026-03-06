"""JenkinsTool — fetches CI build logs from a Jenkins instance."""
import os
import requests
from tools.base_tool import BaseTool


class JenkinsTool(BaseTool):
    """Wraps the Jenkins REST API for log retrieval."""

    def __init__(self, base_url: str = "") -> None:
        super().__init__(name="JenkinsTool")
        self.base_url = base_url or os.getenv("JENKINS_URL", "")

    def health_check(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/json", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def fetch_ci_logs(self, job: str = "qaops", build: str = "lastBuild") -> str:
        """Fetch console output for a Jenkins build."""
        with self.tracer.start_as_current_span("jenkins.fetch_ci_logs"):
            if not self.base_url:
                self.logger.warning("[JenkinsTool] JENKINS_URL not set — returning mock logs")
                return self._mock_logs()
            url = f"{self.base_url}/job/{job}/{build}/consoleText"
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                return resp.text
            except Exception as exc:
                self.logger.error(f"[JenkinsTool] Failed to fetch logs: {exc}")
                return self._mock_logs()

    @staticmethod
    def _mock_logs() -> str:
        return (
            "[INFO] Starting test suite...\n"
            "[ERROR] test_login FAILED\n"
            "  AssertionError: Expected 200, got 500\n"
            "[ERROR] test_checkout FAILED\n"
            "  TimeoutError: DB connection timeout after 30s\n"
        )


# ---------------------------------------------------------------------------
# Module-level helper kept for backward compatibility with existing callers
# ---------------------------------------------------------------------------
def fetch_ci_logs() -> str:
    return JenkinsTool().fetch_ci_logs()