from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobIngestRequest(BaseModel):
    website: str = Field(..., max_length=50)
    job_title: str = Field(..., max_length=255)
    company: str = Field(..., max_length=255)
    location: str | None = Field(None, max_length=255)
    job_description: str
    post_datetime: datetime | None = None
    source_url: str | None = None
    search_keyword: str | None = Field(None, max_length=255)
    search_location: str | None = Field(None, max_length=255)

    @field_validator("website", "job_title", "company", "job_description", mode="before")
    @classmethod
    def _strip_and_reject_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("location", "source_url", "search_keyword", "search_location", mode="before")
    @classmethod
    def _strip_optional(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v if v else None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "website": "linkedin",
                "job_title": "Software Engineer",
                "company": "Google",
                "location": "Vancouver, BC",
                "job_description": "Full original job content here...",
                "post_datetime": "2026-02-27T10:00:00Z",
                "source_url": "https://linkedin.com/job/123",
                "search_keyword": "Software Engineer",
                "search_location": "Vancouver",
            }
        }
    )


class JobIngestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    website: str
    job_title: str
    company: str
    created_at: datetime
