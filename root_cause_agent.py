from adk import Agent, Message
from typing import Dict
from utils.logger import get_logger
import os

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class RootCauseAnalyzerAgent(Agent):
    """
    Agent that uses LLM (Gemini) to summarize root causes of test failures.
    """
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.logger = get_logger(self.__class__.__name__)

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if GENAI_AVAILABLE and api_key:
            self.client = genai.Client(api_key=api_key)
            self.logger.info("Gemini client initialized successfully")
        else:
            self.client = None
            self.logger.warning("Gemini not available or API key missing, using mock analysis")

    def process(self, message: Message) -> Message:
        failed_tests = message.content["failed_tests"]

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Summarize root causes from logs: {failed_tests}"
                )
                analysis_text = response.text
            except Exception as e:
                self.logger.error(f"Gemini API error: {e}")
                analysis_text = f"Fallback analysis due to error: {failed_tests}"
        else:
            analysis_text = f"Mock analysis: Failed tests {failed_tests} likely due to timeout or configuration issues"

        self.logger.info(f"Analysis completed: {analysis_text[:100]}...")
        return Message(
            sender=self.name,
            receiver="ActionPlannerAgent",
            content={"analysis": analysis_text}
        )
