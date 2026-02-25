from __future__ import annotations

import re
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_YYYY_MM_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _parse_month(value: str | date) -> date:
    """Accept ``YYYY-MM`` strings and convert to ``YYYY-MM-01`` date."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        if _YYYY_MM_RE.match(value):
            return date.fromisoformat(f"{value}-01")
        return date.fromisoformat(value)
    raise ValueError("Expected a date or YYYY-MM string")


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

class EducationCreate(BaseModel):
    institution_name: str = Field(..., max_length=255)
    degree: str = Field(..., max_length=255)
    field_of_study: str = Field(..., max_length=255)
    address_country: str = Field(..., max_length=100)
    address_province_state: str = Field(..., max_length=100)
    address_city: str = Field(..., max_length=100)
    start_date: date
    graduate_date: date
    gpa: str | None = Field(None, max_length=20)
    description: str | None = None

    @field_validator("start_date", "graduate_date", mode="before")
    @classmethod
    def _parse_date(cls, v: str | date) -> date:
        return _parse_month(v)

    @model_validator(mode="after")
    def _graduate_after_start(self) -> EducationCreate:
        if self.graduate_date < self.start_date:
            raise ValueError("graduate_date must be >= start_date")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "institution_name": "University of Toronto",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "address_country": "Canada",
                "address_province_state": "Ontario",
                "address_city": "Toronto",
                "start_date": "2018-09",
                "graduate_date": "2022-06",
                "gpa": "3.8",
                "description": "Dean's list, capstone project on NLP",
            }
        }
    )


class EducationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    institution_name: str
    degree: str
    field_of_study: str
    address_country: str
    address_province_state: str
    address_city: str
    start_date: date
    graduate_date: date
    gpa: str | None
    description: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Work Experience
# ---------------------------------------------------------------------------

class WorkExperienceCreate(BaseModel):
    company_name: str = Field(..., max_length=255)
    job_title: str = Field(..., max_length=255)
    location_country: str | None = Field(None, max_length=100)
    location_province_state: str | None = Field(None, max_length=100)
    location_city: str | None = Field(None, max_length=100)
    start_date: date
    end_date: date | None = None
    description: str

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def _parse_date(cls, v: str | date | None) -> date | None:
        if v is None:
            return None
        return _parse_month(v)

    @model_validator(mode="after")
    def _end_after_start(self) -> WorkExperienceCreate:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_name": "Google",
                "job_title": "Software Engineer",
                "location_country": "United States",
                "location_province_state": "California",
                "location_city": "Mountain View",
                "start_date": "2022-07",
                "end_date": None,
                "description": "Full-stack development on Cloud Platform",
            }
        }
    )


class WorkExperienceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_name: str
    job_title: str
    location_country: str | None
    location_province_state: str | None
    location_city: str | None
    start_date: date
    end_date: date | None
    description: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    project_title: str = Field(..., max_length=255)
    start_date: date
    end_date: date | None = None
    description: str

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def _parse_date(cls, v: str | date | None) -> date | None:
        if v is None:
            return None
        return _parse_month(v)

    @model_validator(mode="after")
    def _end_after_start(self) -> ProjectCreate:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_title": "AI Job Hunting Assistant",
                "start_date": "2025-01",
                "end_date": None,
                "description": "End-to-end career strategist platform",
            }
        }
    )


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_title: str
    start_date: date
    end_date: date | None
    description: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

class SkillCreate(BaseModel):
    skill_name: str = Field(..., max_length=100)
    skill_category: str = Field(..., max_length=50)

    @field_validator("skill_category")
    @classmethod
    def _validate_category(cls, v: str) -> str:
        allowed = {"language", "framework", "database", "tooling", "machine_learning", "soft_skill"}
        if v not in allowed:
            raise ValueError(f"skill_category must be one of {sorted(allowed)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skill_name": "Python",
                "skill_category": "language",
            }
        }
    )


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_name: str
    skill_category: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Profile (top-level aggregate)
# ---------------------------------------------------------------------------

class ProfileCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=30)
    linkedin_url: str | None = None
    github_url: str | None = None
    personal_website: str | None = None
    location_country: str | None = Field(None, max_length=100)
    location_province_state: str | None = Field(None, max_length=100)
    location_city: str | None = Field(None, max_length=100)

    educations: list[EducationCreate] = Field(..., min_length=1)
    work_experiences: list[WorkExperienceCreate] = Field(default_factory=list)
    projects: list[ProjectCreate] = Field(default_factory=list)
    skills: list[SkillCreate] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "phone": "+1-416-555-0100",
                "linkedin_url": "https://linkedin.com/in/janedoe",
                "github_url": "https://github.com/janedoe",
                "personal_website": "https://janedoe.dev",
                "location_country": "Canada",
                "location_province_state": "Ontario",
                "location_city": "Toronto",
                "educations": [
                    {
                        "institution_name": "University of Toronto",
                        "degree": "Bachelor of Science",
                        "field_of_study": "Computer Science",
                        "address_country": "Canada",
                        "address_province_state": "Ontario",
                        "address_city": "Toronto",
                        "start_date": "2018-09",
                        "graduate_date": "2022-06",
                        "gpa": "3.8",
                        "description": "Dean's list",
                    }
                ],
                "work_experiences": [
                    {
                        "company_name": "Google",
                        "job_title": "Software Engineer",
                        "location_country": "United States",
                        "location_province_state": "California",
                        "location_city": "Mountain View",
                        "start_date": "2022-07",
                        "end_date": None,
                        "description": "Full-stack development",
                    }
                ],
                "projects": [
                    {
                        "project_title": "AI Job Hunting Assistant",
                        "start_date": "2025-01",
                        "end_date": None,
                        "description": "Career strategist platform",
                    }
                ],
                "skills": [
                    {"skill_name": "Python", "skill_category": "language"},
                    {"skill_name": "FastAPI", "skill_category": "framework"},
                ],
            }
        }
    )


class ProfileUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    linkedin_url: str | None = None
    github_url: str | None = None
    personal_website: str | None = None
    location_country: str | None = Field(None, max_length=100)
    location_province_state: str | None = Field(None, max_length=100)
    location_city: str | None = Field(None, max_length=100)

    educations: list[EducationCreate] | None = None
    work_experiences: list[WorkExperienceCreate] | None = None
    projects: list[ProjectCreate] | None = None
    skills: list[SkillCreate] | None = None

    @field_validator("educations")
    @classmethod
    def _at_least_one_education(cls, v: list[EducationCreate] | None) -> list[EducationCreate] | None:
        if v is not None and len(v) == 0:
            raise ValueError("educations list cannot be empty when provided")
        return v


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    phone: str | None
    linkedin_url: str | None
    github_url: str | None
    personal_website: str | None
    location_country: str | None
    location_province_state: str | None
    location_city: str | None
    created_at: datetime
    updated_at: datetime

    educations: list[EducationResponse]
    work_experiences: list[WorkExperienceResponse]
    projects: list[ProjectResponse]
    skills: list[SkillResponse]
