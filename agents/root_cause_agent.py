"""
RootCauseAnalyzerAgent — LLM + memory-driven root-cause analysis.
"""
import os
from adk import Message
from agents.base_agent import BaseAgent
from utils.llm_factory import run_llm
from utils.memory_handler import query_memory


class RootCauseAnalyzerAgent(BaseAgent):
    """Uses Gemini LLM and memory bank to analyse CI failures."""

    def __init__(self, name: str = "RootCauseAnalyzerAgent"):
        super().__init__(name=name, version="1.1.0")
        self.model = os.getenv("LLM_MODEL", "gemini/gemini-2.5-flash-lite")

    def _run(self, message: Message) -> Message:
        diagnostics: dict = message.content
        failed_tests: list = diagnostics.get("failed_tests", [])
        error_categories: list = diagnostics.get("error_categories", [])
        raw_logs: str = diagnostics.get("raw_logs", "")

        # Pull recurring-pattern context from persistent memory (per test name)
        memory_context = {
            test: query_memory(test)
            for test in failed_tests
            if query_memory(test) is not None
        }

        prompt = (
            "You are a senior QA engineer. Analyse the following CI/CD failure:\n\n"
            f"Failed Tests: {failed_tests}\n"
            f"Error Categories: {error_categories}\n"
            f"Historical Context: {memory_context}\n"
            f"Log snippet:\n{raw_logs[:2000]}\n\n"
            "Return: root_causes (list), brief analysis (str), confidence 0-1."
        )

        with self.tracer.start_as_current_span("llm_root_cause_analysis"):
            try:
                analysis_text: str = run_llm(prompt, self.model)
            except Exception as exc:
                self.logger.error(f"LLM error: {exc}")
                analysis_text = f"Fallback analysis — failed tests: {failed_tests}"

        self.logger.info(f"Analysis (first 100 chars): {analysis_text[:100]}...")

        return Message(
            sender=self.name,
            receiver="ActionPlannerAgent",
            content={
                "analysis": analysis_text,
                "root_causes": failed_tests,
                "confidence": 0.85,
                "error_categories": error_categories,
                "memory_context": memory_context,
            },
        )