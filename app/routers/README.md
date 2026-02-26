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
| [`profile_router.py`](profile_router.py) | Profile CRUD endpoints under `/profiles`. **`GET /profiles`** → list all profiles (summary with id + email). **`POST /profiles`** → creates a full profile (201). **`GET /profiles/{id}`** → returns nested profile (200) or 404. **`PUT /profiles/{id}`** → updates profile and replaces child lists (200). **`DELETE /profiles/{id}`** → deletes profile with cascade (200). |
| [`education_router.py`](education_router.py) | Education CRUD endpoints under `/profiles/{id}/educations`. Full CRUD: list, get, create (201), update (partial), delete. |
| [`work_experience_router.py`](work_experience_router.py) | Work experience CRUD endpoints under `/profiles/{id}/work-experiences`. Full CRUD: list, get, create (201), update (partial), delete. |
| [`project_router.py`](project_router.py) | Project CRUD endpoints under `/profiles/{id}/projects`. Full CRUD: list, get, create (201), update (partial), delete. |

## Endpoint Summary

### `/profiles`

| Method | Path | Status Codes | Description |
|---|---|---|---|
| `GET` | `/profiles` | 200 | List all profiles (summary) |
| `POST` | `/profiles` | 201, 400, 409 | Create full profile |
| `GET` | `/profiles/{id}` | 200, 404 | Get profile by ID |
| `PUT` | `/profiles/{id}` | 200, 400, 404, 409 | Update profile |
| `DELETE` | `/profiles/{id}` | 200, 404 | Delete profile |

### `/profiles/{id}/educations`

| Method | Path | Status Codes |
|---|---|---|
| `GET` | `.../educations` | 200, 404 |
| `POST` | `.../educations` | 201, 400, 404 |
| `GET` | `.../educations/{eid}` | 200, 404 |
| `PUT` | `.../educations/{eid}` | 200, 400, 404, 422 |
| `DELETE` | `.../educations/{eid}` | 200, 404 |

### `/profiles/{id}/work-experiences`

| Method | Path | Status Codes |
|---|---|---|
| `GET` | `.../work-experiences` | 200, 404 |
| `POST` | `.../work-experiences` | 201, 400, 404 |
| `GET` | `.../work-experiences/{wid}` | 200, 404 |
| `PUT` | `.../work-experiences/{wid}` | 200, 400, 404, 422 |
| `DELETE` | `.../work-experiences/{wid}` | 200, 404 |

### `/profiles/{id}/projects`

| Method | Path | Status Codes |
|---|---|---|
| `GET` | `.../projects` | 200, 404 |
| `POST` | `.../projects` | 201, 400, 404 |
| `GET` | `.../projects/{pid}` | 200, 404 |
| `PUT` | `.../projects/{pid}` | 200, 400, 404, 422 |
| `DELETE` | `.../projects/{pid}` | 200, 404 |
