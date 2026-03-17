"""
BaseAgent — abstract foundation for all QAOps pipeline agents.

Extends google.adk.agents.BaseAgent (Pydantic model) to integrate natively
with the Google ADK runner while preserving the existing synchronous
WorkflowGraph interface (process() → _run()).

Provides:
- Google ADK native async interface (_run_async_impl)
- Backward-compatible synchronous interface (process() → _run())
- OpenTelemetry span-level tracing per agent execution
- Structured logging with correlation IDs
- Input/output Message validation
- Agent registry metadata for introspection
"""
from __future__ import annotations

import json
from abc import abstractmethod
from typing import Any, AsyncGenerator

from google.adk.agents import BaseAgent as _ADKBaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from opentelemetry import trace
from pydantic import PrivateAttr

from adk import Message
from utils.logger import get_logger


class BaseAgent(_ADKBaseAgent):
    """
    Abstract base for all QAOps pipeline agents.

    Integrates Google ADK (async _run_async_impl) with the existing
    synchronous WorkflowGraph pipeline (process() → _run()).

    Subclasses MUST implement _run(message) → Message.
    """

    # Declared Pydantic field so it's accepted by model's __init__
    version: str = "1.0.0"

    # Private runtime attributes — not part of the Pydantic schema
    _logger: Any = PrivateAttr(default=None)
    _tracer: Any = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        """Initialise runtime attributes after Pydantic construction."""
        self._logger = get_logger(self.name)
        self._tracer = trace.get_tracer(self.name)

    # ── Google ADK async interface ────────────────────────────────────────────

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Google ADK entry point.

        Reads the previous agent's output from session state (key:
        ``_qaops_message``), delegates to the synchronous _run(), stores the
        result back into session state, and yields the result as an ADK Event.
        """
        # -- Deserialise incoming message from session state or user content --
        state = ctx.session.state
        if "_qaops_message" in state:
            raw = state["_qaops_message"]
            incoming = Message(
                sender=raw.get("sender", "previous_agent"),
                receiver=self.name,
                content=raw.get("content", {}),
            )
        elif ctx.user_content and ctx.user_content.parts:
            try:
                raw = json.loads(ctx.user_content.parts[0].text)
                incoming = Message(
                    sender=raw.get("sender", "user"),
                    receiver=self.name,
                    content=raw.get("content", ctx.user_content.parts[0].text),
                )
            except (json.JSONDecodeError, TypeError):
                incoming = Message(
                    sender="user",
                    receiver=self.name,
                    content={"logs": ctx.user_content.parts[0].text},
                )
        else:
            incoming = Message("system", self.name, {})

        try:
            result: Message = self._run(incoming)
        except Exception as exc:
            self._logger.error(f"[{self.name}] _run failed: {exc}", exc_info=True)
            raise

        # -- Store result in session state for the next agent -----------------
        ctx.session.state["_qaops_message"] = {
            "sender": result.sender,
            "receiver": result.receiver,
            "content": result.content,
        }

        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part(text=json.dumps(result.content, default=str))],
            ),
        )

    # ── Synchronous WorkflowGraph interface (unchanged) ──────────────────────

    @abstractmethod
    def _run(self, message: Message) -> Message:
        """Core agent logic. Must be implemented by subclasses."""
        ...

    def process(self, message: Message) -> Message:
        """
        Public entry point called by WorkflowGraph.
        Wraps _run() with an OTel span, structured logging,
        and exception capture.
        """
        with self._tracer.start_as_current_span(f"{self.name}.process") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("agent.version", self.version)
            span.set_attribute("message.sender", str(message.sender))
            self._logger.info(f"[{self.name}] Starting — from='{message.sender}'")
            try:
                result = self._run(message)
                span.set_attribute("agent.status", "success")
                self._logger.info(f"[{self.name}] Completed successfully")
                return result
            except Exception as exc:
                span.record_exception(exc)
                span.set_attribute("agent.status", "error")
                self._logger.error(f"[{self.name}] Failed: {exc}", exc_info=True)
                raise

    def describe(self) -> dict:
        """Returns agent metadata for registry / debug introspection."""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.__class__.__name__,
        }