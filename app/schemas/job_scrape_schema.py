from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScrapeRequest(BaseModel):
    website: str = Field(..., max_length=50)
    job_title: str = Field(..., max_length=255)
    location: str = Field(..., max_length=255)
    date_posted_filter: str | None = Field(None, max_length=50)
    max_results: int = Field(20, ge=1, le=100)

    @field_validator("website", "job_title", "location", mode="before")
    @classmethod
    def _strip_and_reject_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "website": "linkedin",
                "job_title": "Software Engineer",
                "location": "Vancouver, BC",
                "date_posted_filter": "past_24h",
                "max_results": 20,
            }
        }
    )


class ScrapeResponse(BaseModel):
    message: str
    website: str
    status: str
