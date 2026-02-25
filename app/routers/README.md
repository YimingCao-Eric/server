# app/routers/

FastAPI route handlers.

---

**Navigation:** [< Back to app/](../README.md) | [<< Back to Root](../../README.md) | **Siblings:** [db/](../db/README.md) · [models/](../models/README.md) · [schemas/](../schemas/README.md) · [services/](../services/README.md)

---

## Purpose

This package defines the API endpoints. Routers are intentionally thin — they receive the HTTP request, inject the database session via `Depends(get_session)`, call the appropriate service function, and return the response.

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package marker. |
| [`profile_router.py`](profile_router.py) | Profile CRUD endpoints under `/profiles`. **`POST /profiles`** → creates a full profile (201). **`GET /profiles/{id}`** → returns nested profile (200) or 404. **`PUT /profiles/{id}`** → updates profile and replaces child lists (200). **`DELETE /profiles/{id}`** → deletes profile with cascade (200). All endpoints use typed Pydantic schemas for request validation and response serialization. |

## Endpoint Summary

| Method | Path | Status Codes | Description |
|---|---|---|---|
| `POST` | `/profiles` | 201, 400, 409 | Create full profile |
| `GET` | `/profiles/{id}` | 200, 404 | Get profile by ID |
| `PUT` | `/profiles/{id}` | 200, 400, 404, 409 | Update profile |
| `DELETE` | `/profiles/{id}` | 200, 404 | Delete profile |
