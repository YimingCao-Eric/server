from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class JobApplicationCreate(BaseModel):
    job_title: str
    company_name: str
    apply_url: HttpUrl
    date_year: int
    date_month: int = Field(ge=1, le=12)
    date_day: int = Field(ge=1, le=31)
    job_description: str
    yoe: int = 0
    skill_set: list[str] = Field(default_factory=list)


class JobApplicationUpdate(BaseModel):
    interview: bool | None = None
    offer: bool | None = None
    rejected: bool | None = None


class JobApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_title: str
    company_name: str
    apply_url: str
    date_year: int
    date_month: int
    date_day: int
    job_description: str
    yoe: int
    skill_set: list[str]
    interview: bool
    offer: bool
    rejected: bool
    created_at: datetime
    updated_at: datetime


class DedupRequest(BaseModel):
    urls: list[str]  # URLs from today's search results (max 50)


class DedupResponse(BaseModel):
    new_urls: list[str]
    already_applied: list[str]
    total_input: int
    new_count: int
    applied_count: int


class ApplicationCountResponse(BaseModel):
    count: int
