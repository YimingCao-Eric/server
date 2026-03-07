from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobIngestRequest(BaseModel):
    website: str = Field(..., max_length=50)
    job_title: str = Field(..., max_length=255)
    company: str = Field(..., max_length=255)
    location: str | None = Field(None, max_length=255)
    job_description: str
    post_datetime: datetime | None = None
    job_url: str | None = None  # renamed from source_url
    apply_url: str | None = None
    easy_apply: bool = False
    search_keyword: str | None = Field(None, max_length=255)
    search_location: str | None = Field(None, max_length=255)

    @field_validator("website", "job_title", "company", "job_description", mode="before")
    @classmethod
    def _strip_and_reject_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("location", "job_url", "apply_url", "search_keyword", "search_location", mode="before")
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
                "job_url": "https://linkedin.com/job/123",
                "search_keyword": "Software Engineer",
                "search_location": "Vancouver",
            }
        }
    )


class JobIngestResponse(BaseModel):
    id: uuid.UUID
    already_exists: bool


class JobMatchResultWrite(BaseModel):
    job_id: UUID
    match_level: str
    # allowed values: fully_matched | half_matched | little_matched | irrelevant
    match_reason: str
    extracted_skills: list[str]
    extracted_education: str
    # allowed values: bachelor | master | phd | none
    extracted_yoe: int | None
    # skipped_reason removed — match_reason already encodes gate name


class JobMatchResultResponse(BaseModel):
    job_id: UUID
    stored: bool
    matched_at: datetime


class JobMatchRequest(BaseModel):
    job_ids: list[UUID]  # max 50 - validation can be added
    profile_id: UUID
    force_rematch: bool = False


class JobMatchResult(BaseModel):
    job_id: UUID
    match_level: str
    match_reason: str
    already_matched: bool
    skipped_reason: str | None = None


class JobMatchResponse(BaseModel):
    results: list[JobMatchResult] = Field(default_factory=list)
    total: int = 0
    fully_matched: int = 0
    half_matched: int = 0
    little_matched: int = 0
    irrelevant: int = 0
    skipped: int = 0


class JobRecommendation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_title: str
    company: str
    location: str
    job_url: str | None
    match_level: str
    match_reason: str
    post_datetime: datetime | None


class SkillHistogramItem(BaseModel):
    skill: str
    count: int
