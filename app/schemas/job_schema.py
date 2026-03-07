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
    skipped_reason: str | None = None  # salary_gate, critical_skills_gate, etc.


class JobMatchResultResponse(BaseModel):
    job_id: UUID
    stored: bool
    matched_at: datetime


class JobMatchResultBatchItem(BaseModel):
    """Single item for POST /jobs/match-results/batch."""

    job_id: UUID
    match_level: str
    match_reason: str
    confidence: str | None = None
    fit_score: float | None = None
    req_coverage: float | None = None
    extracted_skills: list[str] = Field(default_factory=list)
    required_skills: list | None = None
    nice_to_have_skills: list | None = None
    critical_skills: list | None = None
    extracted_yoe: float | None = None
    extracted_education: str | None = None
    education_field: str | None = None
    seniority_level: str | None = None
    remote_type: str | None = None
    visa_required: bool | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    job_type: str | None = None
    industry: str | None = None
    jd_incomplete: bool = False
    skipped_reason: str | None = None


class JobMatchResultBatchResponse(BaseModel):
    updated: int
    failed: list[str]  # job_ids that were not found


class JobPartialUpdate(BaseModel):
    """Partial update for PUT /jobs/{job_id}."""

    dismissed: bool | None = None
    recurring_unapplied: bool | None = None
    is_active: bool | None = None


class JobUpdateResponse(BaseModel):
    id: UUID
    updated: bool


class BatchDismissRequest(BaseModel):
    job_ids: list[UUID]


class BatchDismissResponse(BaseModel):
    dismissed: int


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


class JobReviewResponse(BaseModel):
    """Response for GET /jobs filtered review queries (Step 3)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_title: str
    company: str
    location: str | None
    match_level: str | None
    fit_score: float | None
    req_coverage: float | None
    skipped_reason: str | None
    extracted_yoe: float | None
    seniority_level: str | None
    required_skills: list | None
    critical_skills: list | None
    salary_min: float | None
    salary_max: float | None
    dismissed: bool
    created_at: datetime
    job_url: str | None
    easy_apply: bool


class MatchResultsSummary(BaseModel):
    """Response for GET /jobs/match-results/summary."""

    total_scraped: int
    total_deduped: int
    gate_breakdown: dict[str, int]
    match_level_counts: dict[str, int]
