from adk import Agent, Message
from typing import Dict
from utils.logger import get_logger
import os
from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name="multiagent-orchestrator")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class RootCauseAnalyzerAgent(Agent):
    """
    Agent that uses LLM (OpenAI) to summarize root causes of test failures.
    """
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.logger = get_logger(self.__class__.__name__)

        api_key = os.getenv("OPENAI_API_KEY")

        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key
            self.logger.info("OpenAI client initialized successfully")
        else:
            self.logger.warning("OpenAI not available or API key missing, using mock analysis")

    def process(self, message: Message) -> Message:
        failed_tests = message.content["failed_tests"]


        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert QA root cause analyst."},
                        {"role": "user", "content": f"Summarize root causes from logs: {failed_tests}"}
                    ]
                )
                analysis_text = completion.choices[0].message["content"]
            except Exception as e:
                self.logger.error(f"OpenAI API error: {e}")
                analysis_text = f"Fallback analysis due to error: {failed_tests}"
        else:
            analysis_text = f"Mock analysis: Failed tests {failed_tests} likely due to timeout or configuration issues"

        self.logger.info(f"Analysis completed: {analysis_text[:100]}...")
        return Message(
            sender=self.name,
            receiver="ActionPlannerAgent",
            content={"analysis": analysis_text}
        )
