#!/usr/bin/env python3
"""
Training script for QAOps Multi-Agent System
Trains agents and saves model artifacts
"""

import json
from pathlib import Path
from agents.test_diagnostics_agent import TestDiagnosticsAgent
from agents.root_cause_agent import RootCauseAnalyzerAgent
from agents.action_planner_agent import ActionPlannerAgent
from utils.logger import get_logger

def train_agents():
    """Initialize and configure agents"""
    logger = get_logger("TrainingPipeline")
    
    # Initialize agents
    agents = {
        'diagnostics': TestDiagnosticsAgent("TestDiagnostics"),
        'root_cause': RootCauseAnalyzerAgent("RootCause"),
        'action_planner': ActionPlannerAgent("ActionPlanner")
    }
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Save agent configurations only (NOT agent objects)
    agent_config = {
        'version': '1.0',
        'agents': list(agents.keys()),
        'trained_at': str(Path.cwd()),
        'note': 'Agent objects are instantiated at runtime, not pickled'
    }
    
    with open(models_dir / "agent_config.json", "w") as f:
        json.dump(agent_config, f, indent=2)
    
    logger.info("Agents initialized successfully (no pickling required)")
    logger.info(f"Configuration saved to {models_dir / 'agent_config.json'}")
    return models_dir

if __name__ == "__main__":
    train_agents()