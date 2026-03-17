# adk.py — Compatibility shim: maps local adk API → google-adk
from __future__ import annotations

import json
from typing import Any, Dict

# Re-export Google ADK primitives under local names
from google.adk.agents import BaseAgent as Agent                 # noqa: F401
from google.adk.runners import Runner as AgentOrchestrator       # noqa: F401


class Message:
    """
    Local Message — preserved for backward compatibility across the pipeline.
    Converts to/from google.adk Event / types.Content where needed.
    """

    def __init__(self, sender: str, receiver: str, content: Dict[str, Any]):
        self.sender = sender
        self.receiver = receiver
        self.content = content

    # ── Google ADK conversions ────────────────────────────────────────────────

    def to_adk_content(self):
        """Convert local Message → google.genai types.Content (for Runner input)."""
        from google.genai import types
        payload = json.dumps({
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
        })
        return types.Content(
            role="user",
            parts=[types.Part(text=payload)],
        )

    @classmethod
    def from_adk_event(cls, event) -> "Message":
        """Convert a google.adk Event → local Message."""
        try:
            if event.content and event.content.parts:
                raw = json.loads(event.content.parts[0].text)
                return cls(
                    sender=raw.get("sender", getattr(event, "author", "unknown")),
                    receiver=raw.get("receiver", "orchestrator"),
                    content=raw.get("content", {}),
                )
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
        return cls(
            sender=getattr(event, "author", "unknown"),
            receiver="orchestrator",
            content={"text": str(event)},
        )

    def to_dict(self) -> dict:
        return {"sender": self.sender, "receiver": self.receiver, "content": self.content}

    def __repr__(self) -> str:  # pragma: no cover
        return f"Message(sender={self.sender!r}, receiver={self.receiver!r})"


__all__ = ["Message", "Agent", "AgentOrchestrator"]