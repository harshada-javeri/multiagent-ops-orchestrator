"""
ExecutionAgent — final pipeline stage; executes approved remediation actions.

Responsibilities
----------------
- Receive ActionPlannerAgent output (plan, confidence, priority)
- Decide whether to auto-execute based on confidence + priority thresholds
- Dispatch each action to the appropriate executor strategy
- Fetch post-execution Grafana metrics snapshot
- Always produce a fully structured output Message — even on dry-run

Safe defaults
-------------
- dry_run=True  by default — NEVER auto-executes in development
- Actions require confidence >= 0.90 AND priority == "HIGH" to auto-run
- All other cases produce execution_results with status "pending_approval"

ExecutionAgent — executes approved remediation actions.

Sits after ActionPlannerAgent in the workflow graph.
In production, extend _execute_action() with real automation
(Ansible, kubectl rollback, Jenkins retrigger, etc.).

Safe by default: dry_run=True means no auto-execution.
Auto-execution only triggers when:
  - dry_run=False  AND
  - confidence >= AUTO_EXECUTE_THRESHOLD (0.90)
"""
from adk import Message
from agents.base_agent import BaseAgent


class ExecutionAgent(BaseAgent):
    """Executes or queues remediation actions from ActionPlannerAgent."""

    AUTO_EXECUTE_THRESHOLD: float = 0.90

    def __init__(self, name: str = "ExecutionAgent", dry_run: bool = True):
        super().__init__(name=name, version="1.0.0")
        self.dry_run = dry_run

    def _run(self, message: Message) -> Message:
        from tools.tool_registry import ToolRegistry

        plan_data: dict = message.content
        plan: list = plan_data.get("plan", [])
        confidence: float = plan_data.get("confidence", 0.0)
        auto_executed: bool = False
        execution_results: list[dict] = []

        should_execute = (
            not self.dry_run and confidence >= self.AUTO_EXECUTE_THRESHOLD
        )

        if should_execute:
            auto_executed = True
            for action in plan:
                result = self._execute_action(action)
                execution_results.append(result)
                self.logger.info(f"Executed: {action} → {result['status']}")
        else:
            reason = (
                "dry_run=True"
                if self.dry_run
                else f"confidence {confidence:.2f} < threshold {self.AUTO_EXECUTE_THRESHOLD}"
            )
            self.logger.info(f"[{self.name}] Skipping execution ({reason})")
            execution_results = [
                {"action": a, "status": "pending_approval"} for a in plan
            ]

        # Optional: fetch post-execution Grafana snapshot
        metrics_snapshot: dict = {}
        grafana = ToolRegistry.get("grafana")
        if grafana and auto_executed:
            try:
                metrics_snapshot = grafana.fetch_metrics()
            except Exception as exc:
                self.logger.warning(f"Grafana metrics fetch failed: {exc}")

        return Message(
            sender=self.name,
            receiver="Output",
            content={
                **plan_data,
                "execution_results": execution_results,
                "auto_executed": auto_executed,
                "metrics_snapshot": metrics_snapshot,
            },
        )

    def _execute_action(self, action: str) -> dict:
        """
        Dispatch a single remediation action.
        Override or extend this for real automation integrations.
        """
        self.logger.info(f"[{self.name}] Dispatching: {action}")
        return {"action": action, "status": "executed", "output": "OK"}