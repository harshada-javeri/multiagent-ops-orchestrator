# filepath: orchestration/workflow_runner.py
"""
workflow_runner — factory that builds the fully-wired QAOps pipeline graph.

Import build_qaops_graph() in any entry point to get a WorkflowGraph
with all nodes, edges, and the entry node already configured.
"""
import os

from agents.test_diagnostics_agent import TestDiagnosticsAgent
from agents.root_cause_agent import RootCauseAnalyzerAgent
from agents.action_planner_agent import ActionPlannerAgent
from agents.execution_agent import ExecutionAgent
from orchestration.workflow_graph import WorkflowGraph


def build_qaops_graph(dry_run: bool = True) -> WorkflowGraph:
    """
    Build and return the standard QAOps workflow DAG.

    Graph topology:
        diagnostics → root_cause → planner → execution

    Args:
        dry_run: When True, ExecutionAgent will NOT auto-remediate.
                 Reads EXECUTION_DRY_RUN env-var if not explicitly passed.

    Returns:
        WorkflowGraph — call .run(message) to execute the pipeline.
    """
    if dry_run is None:
        dry_run = os.getenv("EXECUTION_DRY_RUN", "true").lower() != "false"

    graph = (
        WorkflowGraph(name="QAOpsPipeline")
        .add_node("diagnostics", TestDiagnosticsAgent())
        .add_node("root_cause",  RootCauseAnalyzerAgent())
        .add_node("planner",     ActionPlannerAgent())
        .add_node("execution",   ExecutionAgent(dry_run=dry_run))
        .add_edge("diagnostics", "root_cause")
        .add_edge("root_cause",  "planner")
        .add_edge("planner",     "execution")
        .set_entry("diagnostics")
    )
    return graph
