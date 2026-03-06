#!/usr/bin/env python3
"""
Prediction script for QAOps Multi-Agent System.
Loads the WorkflowGraph and runs a single inference pass.
"""
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from observability import init_telemetry

init_telemetry("multiagent-orchestrator")

from utils.logger import get_logger
from tools.tool_registry import ToolRegistry
from main_orchestrator import run_qaops_pipeline

logger = get_logger("QAOpsPredictor")

# Bootstrap tools (idempotent if already done by another entry point)
ToolRegistry.bootstrap()


class QAOpsPredictor:
    """
    Thin wrapper kept for backward compatibility.
    predict() now delegates to the WorkflowGraph pipeline.
    """

    def __init__(self, model_path: str = "models") -> None:
        self.logger = get_logger("QAOpsPredictor")
        self.model_path = Path(model_path)
        self.logger.info("QAOpsPredictor ready (WorkflowGraph backend)")

    def predict(self, ci_logs: str) -> dict:
        """
        Run full QAOps pipeline prediction.

        Args:
            ci_logs: Raw CI/CD logs as string.

        Returns:
            dict with analysis, plan, ticket_url, etc.
        """
        try:
            result = run_qaops_pipeline(ci_logs)
            result.setdefault("status", "success")
            result.setdefault("confidence", 0.85)
            return result
        except Exception as exc:
            self.logger.error(f"Prediction failed: {exc}")
            return {"status": "error", "error": str(exc), "confidence": 0.0}


def main() -> None:
    """CLI interface: python predict.py '<ci_logs>'"""
    if len(sys.argv) < 2:
        print("Usage: python predict.py '<ci_logs>'")
        sys.exit(1)

    predictor = QAOpsPredictor()
    result = predictor.predict(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()