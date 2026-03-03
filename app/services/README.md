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
| [`profile_service.py`](profile_service.py) | Top-level profile operations. **`list_profiles()`** — returns all users ordered by creation date. **`create_profile()`** — inserts a `User` and all child records (educations, work experiences, projects, skills) in a single transaction; rolls back and returns `409` on duplicate email. **`get_profile()`** — loads a user with all relationships via `selectinload`; returns `404` if not found. **`update_profile()`** — updates scalar user fields and replaces child lists (clear + re-insert) in one transaction. **`delete_profile()`** — deletes the user; cascade removes all children. |
| [`education_service.py`](education_service.py) | Individual education CRUD operations scoped to a profile. **`list_educations()`** — returns all educations for a profile, ordered by `start_date` descending. **`create_education()`** — adds a single education entry. **`update_education()`** — partial update using `exclude_unset=True`, validates `graduate_date >= start_date` after applying changes. **`delete_education()`** — removes a single education entry. |
| [`work_experience_service.py`](work_experience_service.py) | Individual work experience CRUD scoped to a profile. Same pattern as education_service. Supports the `is_remote` field. Validates `end_date >= start_date` on update. |
| [`project_service.py`](project_service.py) | Individual project CRUD scoped to a profile. Same pattern as education_service. Validates `end_date >= start_date` on update. |
| [`job_service.py`](job_service.py) | Job ingestion logic. **`ingest_job()`** — validates uniqueness using two-tier deduplication: if `source_url` is provided, checks for an existing record with the same URL; otherwise falls back to checking the `(website, job_title, company)` composite. Returns `409 Conflict` on duplicate. Inserts the job in a transaction with rollback on failure. Source-agnostic — no coupling to any specific crawling tool. |
| [`scrape_service.py`](scrape_service.py) | Scrape trigger logic. **`trigger_scrape()`** — validates that the website is supported (linkedin, indeed, glassdoor), resolves webhook URL from env (`SCRAPER_WEBHOOK_LINKEDIN`, etc.), POSTs a JSON payload (job_title, location, date_posted_filter, max_results, ingest_callback_url) via async httpx. Returns `404` if website unsupported or not configured; `503` if the scraper is unreachable or times out. No scraping logic in the backend. |
