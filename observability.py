"""
Observability module for QAOps Multi-Agent System.

Rules:
  - Call init_telemetry() EXACTLY ONCE per process at the entry point.
  - Agent/tool modules MUST NOT call init_telemetry(); they only emit spans.
  - Custom OTel metrics are exposed as module-level counter/histogram objects.
"""
from __future__ import annotations

import os

from monocle_apptrace import setup_monocle_telemetry
from opentelemetry import metrics

from utils.logger import get_logger

logger = get_logger("Observability")

_initialized: bool = False


def init_telemetry(workflow_name: str, environment: str | None = None) -> None:
    """
    Initialise Monocle telemetry. Idempotent — safe to call multiple times.

    Args:
        workflow_name: Logical name visible in Okahu (e.g. 'qaops-prod').
        environment:   Optional env tag; read from ENV_NAME env-var if omitted.
    """
    global _initialized
    if _initialized:
        return

    env = environment or os.getenv("ENV_NAME", "development")
    full_name = (
        f"{workflow_name}-{env}" if env != "development" else workflow_name
    )

    setup_monocle_telemetry(workflow_name=full_name)
    _initialized = True
    logger.info(f"[Observability] Telemetry initialised: workflow='{full_name}'")


# ---------------------------------------------------------------------------
# Pre-built custom metrics — import and increment anywhere in the codebase.
# ---------------------------------------------------------------------------
_meter = metrics.get_meter("qaops")

pipeline_runs = _meter.create_counter(
    name="qaops.pipeline.runs",
    description="Total number of pipeline executions",
    unit="1",
)

pipeline_failures = _meter.create_counter(
    name="qaops.pipeline.failures",
    description="Total number of pipeline failures",
    unit="1",
)

pipeline_duration_ms = _meter.create_histogram(
    name="qaops.pipeline.duration_ms",
    description="End-to-end pipeline execution duration in ms",
    unit="ms",
)

llm_token_usage = _meter.create_counter(
    name="qaops.llm.tokens",
    description="Total LLM tokens consumed across all agents",
    unit="1",
)


if __name__ == "__main__":
    init_telemetry("multiagent-orchestrator")
    logger.info("Telemetry initialised successfully.")