#!/usr/bin/env python3
"""
Prediction script for QAOps Multi-Agent System
Loads trained agents and runs inference
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name="multiagent-orchestrator")

import json
from pathlib import Path
from adk import Message
from agents.test_diagnostics_agent import TestDiagnosticsAgent
from agents.root_cause_agent import RootCauseAnalyzerAgent
from agents.action_planner_agent import ActionPlannerAgent
from utils.logger import get_logger

class QAOpsPredictor:
    def __init__(self, model_path="models"):
        self.logger = get_logger("QAOpsPredictor")
        self.model_path = Path(model_path)
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize agents dynamically at runtime"""
        self.logger.info("Initializing agents...")
        agents = {
            'diagnostics': TestDiagnosticsAgent("TestDiagnostics"),
            'root_cause': RootCauseAnalyzerAgent("RootCause"),
            'action_planner': ActionPlannerAgent("ActionPlanner")
        }
        self.logger.info("Agents initialized successfully")
        return agents
    
    def predict(self, ci_logs: str) -> dict:
        """
        Run full QAOps pipeline prediction
        
        Args:
            ci_logs: Raw CI/CD logs as string
            
        Returns:
            dict: Prediction results with analysis and remediation plan
        """
        try:
            # Step 1: Diagnostics
            diag_message = Message("Input", "TestDiagnostics", ci_logs)
            diag_result = self.agents['diagnostics'].process(diag_message)
            
            # Step 2: Root Cause Analysis
            rca_result = self.agents['root_cause'].process(diag_result)
            
            # Step 3: Action Planning
            action_result = self.agents['action_planner'].process(rca_result)
            
            # Combine results
            prediction = {
                "failed_tests": diag_result.content.get("failed_tests", []),
                "analysis": rca_result.content.get("analysis", ""),
                "remediation_plan": action_result.content.get("plan", ""),
                "ticket_url": action_result.content.get("ticket", ""),
                "confidence": 0.85,
                "status": "success"
            }
            
            self.logger.info("Prediction completed successfully")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }

def main():
    """CLI interface for predictions"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predict.py '<ci_logs>'")
        sys.exit(1)
    
    predictor = QAOpsPredictor()
    logs = sys.argv[1]
    result = predictor.predict(logs)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()