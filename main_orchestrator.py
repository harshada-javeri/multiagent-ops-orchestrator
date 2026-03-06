"""
Main orchestration entry point.

Delegates to WorkflowGraph through EventIngestionLayer + EventRouter.
Backward-compatible: run_qaops_pipeline(ci_logs) still works as before.
"""
from dotenv import load_dotenv

load_dotenv()

# ── Telemetry MUST be initialised before any agent/tool imports ──
from observability import init_telemetry

init_telemetry("multiagent-orchestrator")

from adk import Message  # noqa: E402  (after telemetry init)
from events import EventIngestionLayer, EventRouter  # noqa: E402
from tools.tool_registry import ToolRegistry  # noqa: E402
from utils.logger import get_logger  # noqa: E402

logger = get_logger("MainOrchestrator")

# ── Bootstrap tools once at startup ──────────────────────────────
ToolRegistry.bootstrap()

# ── Wire ingestion → routing ──────────────────────────────────────
_router = EventRouter(dry_run=True)
_ingress = EventIngestionLayer()
_ingress.register_handler(_router)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_qaops_pipeline(ci_logs: str) -> dict:
    """
    Run the QAOps triage pipeline over raw CI log output.

    Args:
        ci_logs: Raw CI/CD console output (string).

    Returns:
        dict with keys: failed_tests, analysis, plan, ticket_url, priority,
                        confidence, execution_results, event_id, …
    """
    return _ingress.ingest_logs(ci_logs, source="manual")


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from tools.jenkins_tool import JenkinsTool

    jenkins = ToolRegistry.get("jenkins")
    logs = jenkins.fetch_ci_logs() if jenkins else "[ERROR] test_login FAILED"

    result = run_qaops_pipeline(logs)
    logger.info(f"Pipeline complete: {result}")
    print(result)