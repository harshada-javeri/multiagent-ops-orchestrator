"""
Main orchestration entry point.

Uses Google ADK SequentialAgent + Runner instead of the custom
EventIngestionLayer/EventRouter, while keeping the public API:
    run_qaops_pipeline(ci_logs) → dict
"""
from dotenv import load_dotenv

load_dotenv()

# ── Telemetry MUST be initialised before any agent/tool imports ──
from observability import init_telemetry

init_telemetry("multiagent-orchestrator")

import asyncio
import json

from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.action_planner_agent import ActionPlannerAgent
from agents.execution_agent import ExecutionAgent
from agents.root_cause_agent import RootCauseAnalyzerAgent
from agents.test_diagnostics_agent import TestDiagnosticsAgent
from adk import Message
from tools.tool_registry import ToolRegistry
from utils.logger import get_logger
from utils.memory_handler import update_memory

logger = get_logger("MainOrchestrator")

# ── Bootstrap tools once at startup ──────────────────────────────
ToolRegistry.bootstrap()

# ── Build Google ADK sequential pipeline ─────────────────────────
_pipeline = SequentialAgent(
    name="qaops_pipeline",
    sub_agents=[
        TestDiagnosticsAgent(),
        RootCauseAnalyzerAgent(),
        ActionPlannerAgent(),
        ExecutionAgent(dry_run=True),
    ],
)

# ── Runner manages sessions + execution lifecycle ─────────────────
_session_service = InMemorySessionService()
_runner = Runner(
    agent=_pipeline,
    app_name="multiagent-orchestrator",
    session_service=_session_service,
)


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
                        confidence, execution_results, …
    """
    async def _run() -> dict:
        session = await _session_service.create_session(
            app_name="multiagent-orchestrator",
            user_id="system",
        )

        initial_content = Message(
            sender="ingress",
            receiver="TestDiagnosticsAgent",
            content={"logs": ci_logs},
        ).to_adk_content()

        last_event = None
        async for event in _runner.run_async(
            user_id="system",
            session_id=session.id,
            new_message=initial_content,
        ):
            # Capture the last agent event (not SequentialAgent state events)
            if event.author and event.author != "qaops_pipeline" and event.content:
                last_event = event

        # Extract result from last agent's event content
        result: dict = {}
        if last_event and last_event.content and last_event.content.parts:
            try:
                result = json.loads(last_event.content.parts[0].text)
            except (json.JSONDecodeError, TypeError):
                result = {"text": str(last_event.content.parts[0].text)}

        # Persist recurring failures to long-term memory
        for test in result.get("failed_tests", []):
            update_memory(test)

        logger.info(f"[MainOrchestrator] Pipeline complete: {list(result.keys())}")
        return result

    return asyncio.run(_run())


# ---------------------------------------------------------------------------
# Standalone execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    jenkins_url = os.getenv("JENKINS_URL", "")
    sample_path = os.path.join("data", "sample_logs", "jenkins_failure.log")

    # Use live Jenkins only when a real URL is configured (not a placeholder)
    if jenkins_url and "your-company" not in jenkins_url and "placeholder" not in jenkins_url:
        jenkins = ToolRegistry.get("jenkins")
        logs = jenkins.fetch_ci_logs() if jenkins else None
        logger.info("[MainOrchestrator] Using Jenkins live logs")
    elif os.path.exists(sample_path):
        with open(sample_path) as f:
            logs = f.read()
        logger.info(f"[MainOrchestrator] Using sample log: {sample_path}")
    else:
        logs = "[ERROR] test_login FAILED\ntest_checkout FAILED\nAssertionError: expected 200 got 500"
        logger.warning("[MainOrchestrator] Using hardcoded fallback logs")

    result = run_qaops_pipeline(logs)
    logger.info(f"Pipeline complete: {result}")
    print(result)