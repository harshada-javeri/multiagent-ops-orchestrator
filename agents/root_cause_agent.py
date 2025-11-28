# agents/root_cause_agent.py
from adk import Agent, Message
from google import genai

class RootCauseAnalyzerAgent(Agent):
    def __init__(self):
        super().__init__() 
        self.model = genai.GenerativeModel('gemini-1.5-pro') 

from typing import Dict

class RootCauseAnalyzerAgent(Agent):
    """
    Agent that uses LLM (Gemini) to summarize root causes of test failures.

    Attributes
    ----------
    name : str
        Name of the agent.
    """
    def __init__(self, name: str) -> None:
        """
        Initialize the RootCauseAnalyzerAgent.

        Parameters
        ----------
        name : str
            Name of the agent.
        """
        self.name = name

    def process(self, message: Message):
        failed_tests = message.content["failed_tests"] 
        analysis = self.model.generate_content( 
            f"Summarize root causes from logs: {failed_tests}" 
        ) 
        return Message( 
            sender=self.name, 
            receiver="ActionPlannerAgent", 
            content={"analysis": analysis.text} 
        ) 
# End of agents/root_cause_agent.py