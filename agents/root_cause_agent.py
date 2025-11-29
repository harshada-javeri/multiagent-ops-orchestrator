# agents/root_cause_agent.py
from adk import Agent, Message
from typing import Dict
from utils.logger import get_logger

try:
    import google.generativeai as genai
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
        if GENAI_AVAILABLE:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None
            self.logger.warning("Google Generative AI not available, using mock analysis")

    def process(self, message: Message) -> Message:
        failed_tests = message.content["failed_tests"]
        
        if self.model and GENAI_AVAILABLE:
            try:
                analysis = self.model.generate_content(
                    f"Summarize root causes from logs: {failed_tests}"
                )
                analysis_text = analysis.text
            except Exception as e:
                self.logger.error(f"Gemini API error: {e}")
                analysis_text = f"Mock analysis: Failed tests {failed_tests} likely due to timeout or configuration issues"
        else:
            analysis_text = f"Mock analysis: Failed tests {failed_tests} likely due to timeout or configuration issues"
        
        self.logger.info(f"Analysis completed: {analysis_text[:100]}...")
        return Message(
            sender=self.name,
            receiver="ActionPlannerAgent",
            content={"analysis": analysis_text}
        )
# End of agents/root_cause_agent.py