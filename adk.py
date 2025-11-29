# adk.py - Agent Development Kit
from typing import Any, Dict

class Message:
    """Message object for agent communication."""
    def __init__(self, sender: str, receiver: str, content: Dict[str, Any]):
        self.sender = sender
        self.receiver = receiver
        self.content = content

class Agent:
    """Base agent class."""
    def __init__(self, name: str):
        self.name = name
    
    def process(self, message: Message) -> Message:
        """Process incoming message and return response."""
        raise NotImplementedError("Subclasses must implement process method")