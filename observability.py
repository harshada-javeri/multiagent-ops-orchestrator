"""
Observability module for QAOps Multi-Agent System.

Telemetry is initialized ONCE per process via init_telemetry().
Agent modules should only emit spans/traces and MUST NOT initialize telemetry.
"""

from monocle_apptrace import setup_monocle_telemetry

_initialized = False

def init_telemetry(workflow_name: str):
    global _initialized
    if _initialized:
        return

    setup_monocle_telemetry(workflow_name=workflow_name)
    _initialized = True


if __name__ == "__main__":
    print("Initializing telemetry...")
    init_telemetry("multiagent-orchestrator")
    print("Telemetry initialized successfully.")