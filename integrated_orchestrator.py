#!/usr/bin/env python3
"""
Integrated QAOps Orchestrator — Okahu tracing + AWS AgentCore.
Now delegates pipeline execution to the WorkflowGraph.
"""
from dotenv import load_dotenv

load_dotenv()

from observability import init_telemetry

init_telemetry("multiagent-orchestrator")

from integrations import AgentCoreIntegration, tracer
from main_orchestrator import run_qaops_pipeline
from tools.tool_registry import ToolRegistry
from utils.logger import get_logger

logger = get_logger("IntegratedOrchestrator")
ToolRegistry.bootstrap()


class IntegratedQAOpsOrchestrator:
    """Production orchestrator wiring AgentCore + Okahu tracing."""

    def __init__(self) -> None:
        self.agentcore = AgentCoreIntegration()

    @tracer.trace_agent
    def analyze_with_observability(self, ci_logs: str) -> dict:
        """Analyse CI logs with full Okahu tracing enabled."""
        return run_qaops_pipeline(ci_logs)

    def deploy_to_agentcore(self, payload: dict) -> dict:
        """Forward analysis result through AWS AgentCore gateway."""
        return self.agentcore.invoke_agent(payload)


if __name__ == "__main__":
    orchestrator = IntegratedQAOpsOrchestrator()
    result = orchestrator.analyze_with_observability("[ERROR] test_login FAILED")
    print(result)