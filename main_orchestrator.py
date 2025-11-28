from adk import AgentOrchestrator, Message
from agents import TestDiagnosticsAgent, RootCauseAnalyzerAgent, ActionPlannerAgent
from utils.logger import setup_logger
from utils.telemetry import init_telemetry
from utils.memory_handler import update_memory
from flask import Flask

logger = setup_logger(__name__)
tracer, meter = init_telemetry()
app = Flask(__name__)

def run_qaops_pipeline(ci_logs: str):
    """
    Run the QAOps triage pipeline over CI log output.

    This function orchestrates a multi-agent workflow that:
    - Starts an OpenTelemetry tracing span named "qaops_pipeline".
    - Logs pipeline start and completion.
    - Initializes and runs the AgentOrchestrator with:
        - TestDiagnosticsAgent ("Diagnostics") for failed test detection and log parsing.
        - RootCauseAnalyzerAgent ("RootCause") for root cause analysis of detected issues.
        - ActionPlannerAgent ("ActionPlanner") for remediation planning and recommended actions.
    - Sends an initial system message containing the provided CI logs to kick off the pipeline.
    - Persists recurring failure signals by calling `update_memory` for each identified failed test.

    Parameters:
    - ci_logs (str): Raw CI pipeline logs (e.g., build, test, runner output) used as input for diagnostics.

    Returns:
    - result (Message): The final message produced by the orchestrator, typically containing structured
        diagnostics (e.g., failed_tests, root_causes, suggested_actions) in `result.content`.

    Raises:
    - Exception: Propagates any error that occurs during orchestration after logging it.

    Side Effects:
    - Emits logs via the module-level `logger`.
    - Creates an OpenTelemetry span for distributed tracing.
    - Calls `update_memory(test)` for each detected recurring failed test to update long-term memory.

    Notes:
    - Expects the orchestrator and agents to adhere to a message-passing interface where `content`
        is a serializable structure (e.g., dict) containing pipeline outputs.
    - The presence of the "failed_tests" key in `result.content` triggers memory updates for those tests.
    """
    try:
        with tracer.start_as_current_span("qaops_pipeline"):
            logger.info("Starting QA triage pipeline")
            # Initialize agents
            orchestrator = AgentOrchestrator(agents=[
                TestDiagnosticsAgent(name="Diagnostics"),
                RootCauseAnalyzerAgent(name="RootCause"),
                ActionPlannerAgent(name="ActionPlanner"),
            ])
            # Start orchestration
            initial_message = Message(
                sender="System",
                receiver="Diagnostics",
                content=ci_logs
            )
            result = orchestrator.start(initial_message)
            # Update memory for recurring issues
            if "failed_tests" in result.content:
                for test in result.content["failed_tests"]:
                    update_memory(test)
            logger.info(f"Pipeline completed: {result.content}")
            return result
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise

if __name__ == "__main__":
    from tools.jenkins_tool import fetch_ci_logs
    logs = fetch_ci_logs()
    run_qaops_pipeline(logs)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    from tools.jenkins_tool import fetch_ci_logs
    logs = fetch_ci_logs()
    run_qaops_pipeline(logs)
    app.run(host="0.0.0.0", port=8080)