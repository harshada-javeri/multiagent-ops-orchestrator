#!/usr/bin/env python3
"""
Integrated QAOps Orchestrator with AWS AgentCore and Okahu
"""

from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name="qaops-multiagent-orchestrator")

from predict import QAOpsPredictor
from integrations import AgentCoreIntegration, tracer

class IntegratedQAOpsOrchestrator:
    def __init__(self):
        self.predictor = QAOpsPredictor()
        self.agentcore = AgentCoreIntegration()
    
    @tracer.trace_agent
    def analyze_with_observability(self, ci_logs: str) -> dict:
        """Analyze CI logs with Okahu tracing"""
        return self.predictor.predict(ci_logs)
    
    def deploy_to_agentcore(self, payload: dict) -> dict:
        """Deploy analysis through AWS AgentCore"""
        return self.agentcore.invoke_agent(payload)

if __name__ == "__main__":
    orchestrator = IntegratedQAOpsOrchestrator()
    result = orchestrator.analyze_with_observability("[ERROR] test_login FAILED")
    print(result)