"""
Pydantic schemas for inbound AIOps events.

CIFailureEvent is the canonical event object passed through
the ingestion → router → workflow pipeline.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EventSource(str, Enum):
    JENKINS        = "jenkins"
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI      = "gitlab_ci"
    MANUAL         = "manual"
    WEBHOOK        = "webhook"


class EventSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"


class CIFailureEvent(BaseModel):
    """Canonical inbound CI/CD failure event."""

    event_id:  str           = Field(default_factory=lambda: str(uuid.uuid4()))
    source:    EventSource   = EventSource.MANUAL
    severity:  EventSeverity = EventSeverity.HIGH
    timestamp: datetime      = Field(default_factory=datetime.utcnow)
    ci_logs:   str
    build_url: Optional[str]       = None
    branch:    Optional[str]       = None
    metadata:  Dict[str, Any]      = Field(default_factory=dict)

    class Config:
        use_enum_values = True