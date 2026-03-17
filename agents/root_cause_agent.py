"""
RootCauseAnalyzerAgent — LLM + memory-driven root-cause analysis.
"""
import os
from typing import Any

from pydantic import PrivateAttr

from adk import Message
from agents.base_agent import BaseAgent
from utils.llm_factory import run_llm
from utils.memory_handler import query_memory


class RootCauseAnalyzerAgent(BaseAgent):
    """Uses Gemini LLM and memory bank to analyse CI failures."""

    _model: str = PrivateAttr(default="")

    def __init__(self, name: str = "RootCauseAnalyzerAgent", **kwargs):
        super().__init__(name=name, version="1.1.0", **kwargs)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._model = os.getenv("LLM_MODEL", "gemini/gemini-2.5-flash-lite")

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

        with self._tracer.start_as_current_span("llm_root_cause_analysis"):
            try:
                analysis_text: str = run_llm(prompt, self._model)
            except Exception as exc:
                self._logger.error(f"LLM error: {exc}")
                analysis_text = f"Fallback analysis — failed tests: {failed_tests}"

        self._logger.info(f"Analysis (first 100 chars): {analysis_text[:100]}...")

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