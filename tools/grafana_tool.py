
from typing import Dict
from utils.logger import get_logger

class GrafanaTool:
    """
    Tool for fetching metrics from Grafana.
    """
    def fetch_metrics(self) -> Dict[str, float]:
        logger = get_logger("GrafanaTool")
        metrics = {"MTTR": 42, "SuccessRate": 0.98}
        logger.info(f"Fetched metrics: {metrics}")
        return metrics
