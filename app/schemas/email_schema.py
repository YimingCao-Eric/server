from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class EmailEventType(str, Enum):
    interview_invite = "interview_invite"
    rejection = "rejection"
    offer = "offer"
    unmatched = "unmatched"


class EmailEvent(BaseModel):
    event_type: EmailEventType
    sender: str
    subject: str
    application_id: UUID | None  # None if unmatched
    company_name: str | None  # extracted from email
    updated_flag: str | None  # "interview" | "rejected" | "offer" | None


class EmailScanResponse(BaseModel):
    events: list[EmailEvent]
    total_scanned: int
    interview_count: int
    rejection_count: int
    offer_count: int
    unmatched_count: int
