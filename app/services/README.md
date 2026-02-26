# app/services/

Business logic and database transaction management.

---

**Navigation:** [< Back to app/](../README.md) | [<< Back to Root](../../README.md) | **Siblings:** [db/](../db/README.md) · [models/](../models/README.md) · [schemas/](../schemas/README.md) · [routers/](../routers/README.md)

---

## Purpose

This package contains the service layer — all business logic sits here, keeping routers thin. Services receive an `AsyncSession` and Pydantic schemas, perform database operations within transactions, and raise `HTTPException` on errors.

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package marker. |
| [`profile_service.py`](profile_service.py) | Core profile operations. **`list_profiles()`** — returns all users ordered by creation date (no eager loading). **`create_profile()`** — inserts a `User` and all child records in a single transaction; rolls back and returns `409` on duplicate email. **`get_profile()`** — loads a user with all relationships via `selectinload`; returns `404` if not found. **`update_profile()`** — updates scalar user fields and replaces child lists (clear + re-insert) in one transaction. **`delete_profile()`** — deletes the user; cascade removes all children. |
| [`education_service.py`](education_service.py) | Education CRUD operations scoped to a profile. **`list_educations()`** — returns all educations for a profile ordered by `start_date` desc. **`get_education()`** — returns a single education or 404. **`create_education()`** — adds an education entry. **`update_education()`** — partial update via `exclude_unset`; validates `graduate_date >= start_date`. **`delete_education()`** — removes an education entry. |
| [`work_experience_service.py`](work_experience_service.py) | Work experience CRUD operations scoped to a profile. **`list_work_experiences()`** — returns all work experiences ordered by `start_date` desc. **`get_work_experience()`** — returns a single entry or 404. **`create_work_experience()`** — adds a work experience entry. **`update_work_experience()`** — partial update; validates `end_date >= start_date`. **`delete_work_experience()`** — removes a work experience entry. |
| [`project_service.py`](project_service.py) | Project CRUD operations scoped to a profile. **`list_projects()`** — returns all projects ordered by `start_date` desc. **`get_project()`** — returns a single project or 404. **`create_project()`** — adds a project entry. **`update_project()`** — partial update; validates `end_date >= start_date`. **`delete_project()`** — removes a project entry. |

## Transaction Strategy

```
session.add(user)  →  session.commit()
        ↓ on IntegrityError
session.rollback()  →  raise HTTPException(409)
```
