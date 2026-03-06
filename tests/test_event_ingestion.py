"""
Unit tests for EventIngestionLayer and EventRouter.
No external services or LLM calls.
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from events.event_schema import CIFailureEvent, EventSource, EventSeverity
from events.event_ingestion import EventIngestionLayer


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

def test_event_schema_defaults():
    event = CIFailureEvent(ci_logs="[ERROR] test_login FAILED")
    assert event.source == EventSource.MANUAL
    assert event.severity == EventSeverity.HIGH
    assert event.event_id  # auto-generated UUID
    assert event.ci_logs == "[ERROR] test_login FAILED"


def test_event_schema_custom_fields():
    event = CIFailureEvent(
        ci_logs="[ERROR] test FAILED",
        source="jenkins",
        severity="critical",
        branch="main",
        build_url="https://ci.example.com/build/42",
    )
    assert event.source == "jenkins"
    assert event.severity == "critical"
    assert event.branch == "main"


def test_event_schema_missing_ci_logs():
    with pytest.raises(Exception):
        CIFailureEvent()  # ci_logs is required


# ---------------------------------------------------------------------------
# EventIngestionLayer tests
# ---------------------------------------------------------------------------

def test_ingestion_calls_handler():
    received = []

    def handler(event: CIFailureEvent):
        received.append(event)

    ingress = EventIngestionLayer()
    ingress.register_handler(handler)
    event = ingress.ingest_logs("[ERROR] test_x FAILED", source="manual")

    assert len(received) == 1
    assert received[0].event_id == event.event_id
    assert received[0].ci_logs == "[ERROR] test_x FAILED"


def test_ingestion_multiple_handlers():
    counts = {"a": 0, "b": 0}

    ingress = EventIngestionLayer()
    ingress.register_handler(lambda _: counts.__setitem__("a", counts["a"] + 1))
    ingress.register_handler(lambda _: counts.__setitem__("b", counts["b"] + 1))
    ingress.ingest_logs("dummy logs")

    assert counts["a"] == 1
    assert counts["b"] == 1


def test_ingestion_handler_exception_does_not_propagate():
    """A failing handler must not crash the ingestion layer."""

    def bad_handler(_):
        raise RuntimeError("Simulated handler failure")

    ingress = EventIngestionLayer()
    ingress.register_handler(bad_handler)

    # Should NOT raise
    event = ingress.ingest_logs("[ERROR] test FAILED")
    assert event.event_id  # ingestion still returned a valid event