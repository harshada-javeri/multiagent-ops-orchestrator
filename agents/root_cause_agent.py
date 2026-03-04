
from adk import Agent, Message
from typing import Dict
from utils.logger import get_logger
import os
from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name="multiagent-orchestrator")
from utils.llm_factory import run_llm
from opentelemetry import trace
tracer = trace.get_tracer("RootCauseAnalyzerAgent")



class RootCauseAnalyzerAgent(Agent):
    """
    Agent that uses LiteLLM to summarize root causes of test failures.
    """
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.logger = get_logger(self.__class__.__name__)

    def process(self, message: Message) -> Message:
        failed_tests = message.content["failed_tests"]
        prompt = f"Summarize root causes from logs: {failed_tests}"
        model = os.getenv("LLM_MODEL", "gemini/gemini-2.5-flash-lite")
        with tracer.start_as_current_span("llm_root_cause_analysis"):
            try:
                analysis_text = run_llm(prompt, model)
            except Exception as e:
                self.logger.error(f"LLM error: {e}")
                analysis_text = f"Fallback analysis due to error: {failed_tests}"
        self.logger.info(f"Analysis completed: {analysis_text[:100]}...")
        return Message(
            sender=self.name,
            receiver="ActionPlannerAgent",
            content={"analysis": analysis_text}
        )
