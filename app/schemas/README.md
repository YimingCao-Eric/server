# app/schemas/

Pydantic schemas for request validation and response serialization.

---

**Navigation:** [< Back to app/](../README.md) | [<< Back to Root](../../README.md) | **Siblings:** [db/](../db/README.md) · [models/](../models/README.md) · [services/](../services/README.md) · [routers/](../routers/README.md)

---

## Purpose

This package defines all Pydantic models used by the API layer. Input schemas validate and transform incoming JSON (including `YYYY-MM` → `DATE` conversion). Output schemas serialize SQLAlchemy model instances into structured JSON responses.

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Re-exports all profile schema classes for convenient imports. |
| [`profile.py`](profile.py) | All profile-related schemas. **Create schemas** (`EducationCreate`, `WorkExperienceCreate`, `ProjectCreate`, `SkillCreate`, `ProfileCreate`) validate incoming data — dates accept `YYYY-MM` strings and convert to `YYYY-MM-01`, cross-field validators enforce `graduate_date >= start_date` and `end_date >= start_date`, `skill_category` is constrained to the allowed enum values, and `is_remote` defaults to `false`. `ProfileCreate` requires at least one education entry. **Update schemas** (`EducationUpdate`, `WorkExperienceUpdate`, `ProjectUpdate`, `ProfileUpdate`) make all fields optional for partial updates. **Response schemas** (`EducationResponse`, `WorkExperienceResponse`, `ProjectResponse`, `SkillResponse`, `ProfileSummaryResponse`, `ProfileResponse`) use `from_attributes=True` to serialize directly from ORM objects. `ProfileSummaryResponse` returns only `id` and `email` for list endpoints. All Create schemas include OpenAPI examples visible in Swagger UI. |
| [`job_schema.py`](job_schema.py) | Job ingestion schemas. **`JobIngestRequest`** — validates incoming job postings from external collectors. Required fields: `website`, `job_title`, `company`, `job_description`. Optional: `location`, `post_datetime` (ISO 8601), `source_url`, `search_keyword`, `search_location`. All string fields are whitespace-trimmed; required fields reject empty strings. Includes OpenAPI example. **`JobIngestResponse`** — returns `id`, `website`, `job_title`, `company`, `created_at` after successful ingestion. |

## Date Handling

Incoming date fields in profile schemas accept two formats:

| Input | Stored As |
|---|---|
| `"2022-07"` | `2022-07-01` |
| `"2022-07-15"` | `2022-07-15` |

This is handled by the `_parse_month()` helper and applied via `@field_validator` on all date fields.
