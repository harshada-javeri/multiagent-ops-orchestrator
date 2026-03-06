"""BaseTool — abstract base class for all external tool integrations."""
from abc import ABC, abstractmethod

from opentelemetry import trace

from utils.logger import get_logger


class BaseTool(ABC):
    """
    All tools must extend BaseTool and implement health_check().
    Provides consistent tracing and logging across integrations.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = get_logger(self.name)
        self.tracer = trace.get_tracer(self.name)

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the external service is reachable."""
        ...

    def describe(self) -> dict:
        return {"name": self.name, "type": self.__class__.__name__}