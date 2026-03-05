# app/

Main application package for the AI Job Hunting Assistant backend.

---

## Project Idea (from [overview.md](../overview.md))

A fully automated job hunting system that runs 24/7: searches LinkedIn, scores jobs with LLM matching, tracks applications, monitors email for interview/offer/rejection, and generates weekly reports. The backend is a stable core — it never changes between Phase 1 (OpenClaw), Phase 2 (n8n), and Phase 3 (Python scraper).

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../ (Root)](../README.md) |
| **Next folder** | [core/](core/README.md) |
| **Siblings** | [alembic/](../alembic/README.md) · [scripts/](../scripts/README.md) |

---

## Architecture Flow

```
Request → Router → Service → SQLAlchemy Models → PostgreSQL
                      ↑
              Pydantic Schemas (validate input/output)
```

**Domains:**
- **Profiles** — User professional profile (users, educations, work experiences, projects, skills)
- **Jobs** — Job ingestion, matching, recommendations, skill histogram
- **Applications** — Confirmed applications, URL dedup, flags (interview/offer/rejected)
- **Email** — Gmail scan for interview/offer/rejection classification
- **Reports** — Store and retrieve weekly LLM-generated reports

---

## Files

| File | Description |
|------|-------------|
| [`__init__.py`](__init__.py) | Package marker. Makes `app` importable as a Python package. |
| [`main.py`](main.py) | **FastAPI entry point.** Creates the `FastAPI` instance, includes all routers (profile, education, work experience, project, skill, job, application, email, report), and exposes `GET /health` for container health checks. Run with `uvicorn app.main:app`. **Functions:** `health_check()` — returns `{"status": "ok"}`. |

---

## Subdirectories

| Directory | Description |
|-----------|--------------|
| [**core/**](core/README.md) | Config and settings (database URLs, scraper webhooks, Gmail OAuth2, Anthropic API key). |
| [**db/**](db/README.md) | Database infrastructure — SQLAlchemy base, async engine, session factory. |
| [**models/**](models/README.md) | SQLAlchemy ORM models (User, Education, WorkExperience, Project, Skill, Job, JobApplication). |
| [**schemas/**](schemas/README.md) | Pydantic schemas for request validation and response serialization. |
| [**services/**](services/README.md) | Business logic layer — all DB operations and transactions. |
| [**routers/**](routers/README.md) | FastAPI route handlers — thin layer delegating to services. |
