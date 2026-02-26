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
| [`profile_router.py`](profile_router.py) | Profile CRUD endpoints under `/profiles`. **`GET /profiles`** → lists all profiles returning summary data (id + email). **`POST /profiles`** → creates a full profile (201). **`GET /profiles/{id}`** → returns full nested profile (200) or 404. **`PUT /profiles/{id}`** → updates profile and replaces child lists (200). **`DELETE /profiles/{id}`** → deletes profile with cascade (200). |
| [`education_router.py`](education_router.py) | Education CRUD endpoints under `/profiles/{id}/educations`. Supports list, get, create, update, and delete for individual education entries belonging to a profile. |
| [`work_experience_router.py`](work_experience_router.py) | Work experience CRUD endpoints under `/profiles/{id}/work-experiences`. Supports list, get, create, update, and delete for individual work experience entries belonging to a profile. |
| [`project_router.py`](project_router.py) | Project CRUD endpoints under `/profiles/{id}/projects`. Supports list, get, create, update, and delete for individual project entries belonging to a profile. |

## Endpoint Summary

### Profiles

| Method | Path | Status Codes | Description |
|---|---|---|---|
| `GET` | `/profiles` | 200 | List all profiles (summary) |
| `POST` | `/profiles` | 201, 400, 409 | Create full profile |
| `GET` | `/profiles/{id}` | 200, 404 | Get profile by ID |
| `PUT` | `/profiles/{id}` | 200, 400, 404, 409 | Update profile |
| `DELETE` | `/profiles/{id}` | 200, 404 | Delete profile |

### Educations

| Method | Path | Status Codes | Description |
|---|---|---|---|
| `GET` | `/profiles/{id}/educations` | 200, 404 | List educations |
| `POST` | `/profiles/{id}/educations` | 201, 404 | Create education |
| `GET` | `/profiles/{id}/educations/{edu_id}` | 200, 404 | Get education |
| `PUT` | `/profiles/{id}/educations/{edu_id}` | 200, 404, 422 | Update education |
| `DELETE` | `/profiles/{id}/educations/{edu_id}` | 200, 404 | Delete education |

### Work Experiences

| Method | Path | Status Codes | Description |
|---|---|---|---|
| `GET` | `/profiles/{id}/work-experiences` | 200, 404 | List work experiences |
| `POST` | `/profiles/{id}/work-experiences` | 201, 404 | Create work experience |
| `GET` | `/profiles/{id}/work-experiences/{we_id}` | 200, 404 | Get work experience |
| `PUT` | `/profiles/{id}/work-experiences/{we_id}` | 200, 404, 422 | Update work experience |
| `DELETE` | `/profiles/{id}/work-experiences/{we_id}` | 200, 404 | Delete work experience |

### Projects

| Method | Path | Status Codes | Description |
|---|---|---|---|
| `GET` | `/profiles/{id}/projects` | 200, 404 | List projects |
| `POST` | `/profiles/{id}/projects` | 201, 404 | Create project |
| `GET` | `/profiles/{id}/projects/{proj_id}` | 200, 404 | Get project |
| `PUT` | `/profiles/{id}/projects/{proj_id}` | 200, 404, 422 | Update project |
| `DELETE` | `/profiles/{id}/projects/{proj_id}` | 200, 404 | Delete project |
