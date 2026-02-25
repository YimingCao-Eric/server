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
| [`__init__.py`](__init__.py) | Re-exports all schema classes for convenient imports. |
| [`profile.py`](profile.py) | All profile-related schemas. **Create schemas** (`EducationCreate`, `WorkExperienceCreate`, `ProjectCreate`, `SkillCreate`, `ProfileCreate`, `ProfileUpdate`) validate incoming data — dates accept `YYYY-MM` strings and convert to `YYYY-MM-01`, cross-field validators enforce `graduate_date >= start_date` and `end_date >= start_date`, and `skill_category` is constrained to the allowed enum values. `ProfileCreate` requires at least one education entry. **Response schemas** (`EducationResponse`, `WorkExperienceResponse`, `ProjectResponse`, `SkillResponse`, `ProfileResponse`) use `from_attributes=True` to serialize directly from ORM objects. All schemas include OpenAPI examples visible in Swagger UI. |

## Date Handling

Incoming date fields accept two formats:

| Input | Stored As |
|---|---|
| `"2022-07"` | `2022-07-01` |
| `"2022-07-15"` | `2022-07-15` |

This is handled by the `_parse_month()` helper and applied via `@field_validator` on all date fields.
