"""GrafanaTool — fetches system metrics from a Grafana instance."""
import os
import requests
from tools.base_tool import BaseTool


class GrafanaTool(BaseTool):
    """Wraps the Grafana HTTP API for metrics retrieval."""

    def __init__(self, base_url: str = "") -> None:
        super().__init__(name="GrafanaTool")
        self.base_url = base_url or os.getenv("GRAFANA_URL", "")

    def health_check(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def fetch_metrics(
        self,
        dashboard: str = "ci-overview",
        time_range: str = "1h",
    ) -> dict:
        """Fetch key metrics for the given dashboard and time range."""
        with self.tracer.start_as_current_span("grafana.fetch_metrics"):
            if not self.base_url:
                self.logger.warning("[GrafanaTool] GRAFANA_URL not set — returning mock metrics")
                return self._mock_metrics()
            try:
                resp = requests.get(
                    f"{self.base_url}/api/dashboards/uid/{dashboard}",
                    params={"from": f"now-{time_range}", "to": "now"},
                    timeout=10,
                )
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                self.logger.error(f"[GrafanaTool] Metrics fetch failed: {exc}")
                return self._mock_metrics()

    @staticmethod
    def _mock_metrics() -> dict:
        return {
            "cpu_usage_pct": 72.4,
            "memory_usage_pct": 58.1,
            "p95_latency_ms": 340,
            "error_rate_pct": 3.2,
        }
