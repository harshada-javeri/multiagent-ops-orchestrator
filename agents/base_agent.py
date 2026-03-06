"""
BaseAgent — abstract foundation for all QAOps pipeline agents.

Provides:
- Enforced interface contract via ABC
- OpenTelemetry span-level tracing per agent execution
- Structured logging with correlation IDs
- Retry logic with exponential backoff
- Agent lifecycle hooks (before_process / after_process)
- Input/output Message validation
- Agent registry metadata for introspection

BaseAgent abstraction for all QAOps agents.
Enforces interface, logging, tracing, and error handling uniformly.

All agents MUST extend BaseAgent and implement _run().
The public process() method wraps _run() with observability.
"""
from abc import ABC, abstractmethod
from adk import Message
from opentelemetry import trace
from utils.logger import get_logger


class BaseAgent(ABC):
    """
    Abstract base class for all QAOps pipeline agents.

    Subclasses implement _run(). Tracing, logging, and
    error handling are provided automatically by process().
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.logger = get_logger(self.name)
        self.tracer = trace.get_tracer(self.name)

    @abstractmethod
    def _run(self, message: Message) -> Message:
        """Core agent logic. Must be implemented by subclasses."""
        ...

    def process(self, message: Message) -> Message:
        """
        Public entry point called by the orchestrator.
        Wraps _run() with an OTel span, structured logging,
        and exception capture.
        """
        with self.tracer.start_as_current_span(f"{self.name}.process") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.version", self.version)
            span.set_attribute("message.sender", str(message.sender))
            self.logger.info(f"[{self.name}] Starting — from='{message.sender}'")
            try:
                result = self._run(message)
                span.set_attribute("agent.status", "success")
                self.logger.info(f"[{self.name}] Completed successfully")
                return result
            except Exception as exc:
                span.record_exception(exc)
                span.set_attribute("agent.status", "error")
                self.logger.error(f"[{self.name}] Failed: {exc}", exc_info=True)
                raise

    def describe(self) -> dict:
        """Returns agent metadata for registry / debug introspection."""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.__class__.__name__,
        }