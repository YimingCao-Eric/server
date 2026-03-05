# app/routers/

FastAPI route handlers.

---

## Project Idea (from [overview.md](../../overview.md))

Routers are the HTTP boundary. They receive requests, inject `get_session`, call services, and return validated responses. All endpoints support the 6-step pipeline: ingest, dedup, match, apply, email scan, reports.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../schemas/](schemas/README.md) |
| **Next folder** | [../services/](services/README.md) |
| **Siblings** | [core/](../core/README.md) · [db/](../db/README.md) · [models/](../models/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`profile_router.py`](profile_router.py) | Prefix `/profiles`. **`list_profiles()`** — GET / → list. **`create_profile()`** — POST / → 201. **`get_resume_text()`** — GET /{id}/resume-text → {resume_text, token_estimate}. **`get_profile()`** — GET /{id}. **`update_profile()`** — PUT /{id}. **`delete_profile()`** — DELETE /{id}. |
| [`education_router.py`](education_router.py) | Prefix `/profiles/{profile_id}/educations`. **`list_educations()`**, **`get_education()`**, **`create_education()`**, **`update_education()`**, **`delete_education()`** — full CRUD. |
| [`work_experience_router.py`](work_experience_router.py) | Prefix `/profiles/{profile_id}/work-experiences`. Same CRUD pattern. |
| [`project_router.py`](project_router.py) | Prefix `/profiles/{profile_id}/projects`. Same CRUD pattern. |
| [`skill_router.py`](skill_router.py) | Prefix `/profiles/{profile_id}/skills`. Same CRUD pattern. |
| [`job_router.py`](job_router.py) | Prefix `/jobs`. **`ingest_job()`** — POST /ingest → 200, {id, already_exists}. **`store_match_result()`** — POST /match-results (OpenClaw write-back). **`run_match()`** — POST /match (Phase 2+ backend LLM). **`get_recommendations()`** — GET /recommendations/{profile_id}. **`get_skill_histogram()`** — GET /skill-histogram. **`trigger_scrape()`** — POST /scrape → 202. |
| [`application_router.py`](application_router.py) | Prefix `/jobs/applications`. **`create_application()`** — POST / → 201, 409 on duplicate apply_url. **`dedup_urls()`** — POST /dedup → {new_urls, already_applied, total_input, new_count, applied_count}. **`count_applications()`** — GET /count. **`list_application_urls()`** — GET /urls. **`list_applications()`** — GET / ?limit=&offset=. **`get_application()`** — GET /{id}. **`update_application()`** — PUT /{id} (interview/offer/rejected). |
| [`email_router.py`](email_router.py) | Prefix `/email`. **`scan_email()`** — POST /scan → EmailScanResponse; 503 if Gmail credentials missing. |
| [`report_router.py`](report_router.py) | Prefix `/reports`. **`store_report()`** — POST /store (OpenClaw write-back; in-memory). **`generate_report()`** — POST /generate (backend LLM; Phase 2+). **`get_latest_report()`** — GET /latest; 404 if none stored. |
