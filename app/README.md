# app/

Main application package for the AI Job Hunting Assistant backend.

---

**Navigation:** [< Back to Root](../README.md) | **Sibling:** [alembic/](../alembic/README.md)

---

## Purpose

This package contains the full application code following clean architecture: routers handle HTTP, services contain business logic, schemas validate data, and models define the database structure.

## Architecture Flow

```
Request → Router → Service → SQLAlchemy Models → PostgreSQL
                      ↑
              Pydantic Schemas
              (validate input/output)
```

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package marker. Makes `app` importable as a Python package. |
| [`main.py`](main.py) | FastAPI application entry point. Creates the `FastAPI` instance, includes four routers (profile, education, work experience, project), and exposes a `/health` endpoint. Run with `uvicorn app.main:app`. |

## Subdirectories

| Directory | Description |
|---|---|
| [`db/`](db/README.md) | Database infrastructure — the SQLAlchemy declarative base, metadata configuration, async engine, and session factory. |
| [`models/`](models/README.md) | SQLAlchemy ORM model definitions (User, Education, WorkExperience, Project, Skill). |
| [`schemas/`](schemas/README.md) | Pydantic schemas for request validation and response serialization, including `YYYY-MM` date parsing. |
| [`services/`](services/README.md) | Business logic layer. All database operations and transaction management live here. |
| [`routers/`](routers/README.md) | FastAPI route handlers. Thin layer that delegates to services. |
