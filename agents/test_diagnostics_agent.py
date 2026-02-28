from adk import Agent, Message
from utils.logger import get_logger
from monocle_apptrace import setup_monocle_telemetry
setup_monocle_telemetry(workflow_name="multiagent-orchestrator")

class TestDiagnosticsAgent(Agent):
    __test__ = False
    """
    Agent that parses CI logs to identify failed tests.
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.logger = get_logger(self.__class__.__name__)

    def process(self, message: Message) -> Message:
        """
        Parse logs and extract failed tests.
        """
        logs = message.content
        failed_tests = [line for line in logs.split("\n") if "FAIL" in line]
        self.logger.info(f"Extracted failed tests: {failed_tests}")
        return Message(
            sender=self.name,
            receiver="RootCauseAnalyzerAgent",
            content={"failed_tests": failed_tests}
        )
# End of agents/test_diagnostics_agent.py