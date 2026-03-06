"""
Quick workspace verification script - tests basic functionality without external dependencies
"""

import sys
import os

print("=" * 60)
print("Multi-Agent QAOps Orchestrator - Workspace Verification")
print("=" * 60)
print()

# Test 1: Python Version
print(f"✓ Python Version: {sys.version}")
print()

# Test 2: Import ADK
try:
    from adk import Agent, Message, AgentOrchestrator
    print("✓ ADK imports successfully")
    print(f"  - Agent class: {Agent}")
    print(f"  - Message class: {Message}")
    print(f"  - AgentOrchestrator class: {AgentOrchestrator}")
except Exception as e:
    print(f"✗ ADK import failed: {e}")
    sys.exit(1)

print()

# Test 3: Import Agents
try:
    from agents import TestDiagnosticsAgent, RootCauseAnalyzerAgent, ActionPlannerAgent
    print("✓ All agents import successfully")
    print(f"  - TestDiagnosticsAgent: {TestDiagnosticsAgent}")
    print(f"  - RootCauseAnalyzerAgent: {RootCauseAnalyzerAgent}")
    print(f"  - ActionPlannerAgent: {ActionPlannerAgent}")
except Exception as e:
    print(f"✗ Agents import failed: {e}")
    sys.exit(1)

print()

# Test 4: Import Tools
try:
    from tools import JenkinsTool, JiraTool, GrafanaTool
    print("✓ All tools import successfully")
    print(f"  - JenkinsTool: {JenkinsTool}")
    print(f"  - JiraTool: {JiraTool}")
    print(f"  - GrafanaTool: {GrafanaTool}")
except Exception as e:
    print(f"✗ Tools import failed: {e}")
    sys.exit(1)

print()

# Test 5: Import Utils
try:
    from utils.logger import get_logger
    from utils.memory_handler import update_memory
    print("✓ Utils import successfully")
    print(f"  - get_logger: {get_logger}")
    print(f"  - update_memory: {update_memory}")
except Exception as e:
    print(f"✗ Utils import failed: {e}")
    sys.exit(1)

print()

# Test 6: Create a simple message
try:
    test_msg = Message(
        sender="System",
        receiver="TestAgent",
        content={"test": "data"}
    )
    print("✓ Message creation successful")
    print(f"  - Sender: {test_msg.sender}")
    print(f"  - Receiver: {test_msg.receiver}")
    print(f"  - Content: {test_msg.content}")
except Exception as e:
    print(f"✗ Message creation failed: {e}")
    sys.exit(1)

print()

# Test 7: Verify file structure
print("✓ File structure verification:")
dirs_to_check = ["agents", "tools", "utils", "models", "data", "tests", "docs"]
for dir_name in dirs_to_check:
    exists = os.path.isdir(dir_name)
    status = "✓" if exists else "✗"
    print(f"  {status} {dir_name}/")

print()
print("=" * 60)
print("✓ WORKSPACE VERIFICATION COMPLETE")
print("=" * 60)
print()
print("NOTE: To run the full orchestrator, you need:")
print("  1. Python 3.9 or higher")
print("  2. Install dependencies: pip install -r requirements.txt")
print("  3. Configure environment variables in .env file")
print()
