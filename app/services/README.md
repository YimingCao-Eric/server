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
| [`profile_service.py`](profile_service.py) | Core profile operations. **`create_profile()`** — inserts a `User` and all child records (educations, work experiences, projects, skills) in a single transaction; rolls back and returns `409` on duplicate email. **`get_profile()`** — loads a user with all relationships via `selectinload`; returns `404` if not found. **`update_profile()`** — updates scalar user fields and replaces child lists (clear + re-insert) in one transaction. **`delete_profile()`** — deletes the user; cascade removes all children. All functions use the shared `_load_user()` helper for consistent eager loading and 404 handling. |

## Transaction Strategy

```
session.add(user)  →  session.commit()
        ↓ on IntegrityError
session.rollback()  →  raise HTTPException(409)
```
