# app/services/

Business logic and database transaction management.

---

## Project Idea (from [overview.md](../../overview.md))

Services implement the 6-step pipeline logic: ingest jobs, dedup URLs, store match results, manage applications, scan email, generate/store reports. All DB operations and transactions live here; routers stay thin.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../routers/](routers/README.md) |
| **Next folder** | [../ (app)](../README.md) — *services is last in app chain* |
| **Siblings** | [core/](../core/README.md) · [db/](../db/README.md) · [models/](../models/README.md) · [schemas/](../schemas/README.md) · [routers/](../routers/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`profile_service.py`](profile_service.py) | **`list_profiles()`** — all users by created_at. **`create_profile()`** — insert User + children in one transaction; 409 on duplicate email. **`get_profile()`** — load user with selectinload(educations, work_experiences, projects, skills); 404 if not found. **`update_profile()`** — update scalar fields, replace child lists. **`delete_profile()`** — delete user (cascade). **`get_resume_text()`** — build condensed resume text + token_estimate for OpenClaw (≤500 tokens). |
| [`education_service.py`](education_service.py) | **`list_educations()`**, **`get_education()`**, **`create_education()`**, **`update_education()`**, **`delete_education()`** — CRUD scoped to profile_id. Validates graduate_date >= start_date. |
| [`work_experience_service.py`](work_experience_service.py) | Same CRUD pattern for work experiences. Validates end_date >= start_date. |
| [`project_service.py`](project_service.py) | Same CRUD pattern for projects. |
| [`skill_service.py`](skill_service.py) | Same CRUD pattern for skills. |
| [`job_service.py`](job_service.py) | **`_find_duplicate()`** — by source_url or (website, job_title, company). **`ingest_job()`** — dedup then insert; returns (job, already_exists). **`store_match_result()`** — write OpenClaw match data onto jobs row; 404 if job not found. |
| [`scrape_service.py`](scrape_service.py) | **`_get_webhook_url()`** — resolve webhook from env by website. **`trigger_scrape()`** — POST payload (job_title, location, date_posted_filter, max_results, ingest_callback_url) to webhook; 404 if not configured, 503 if unreachable. |
| [`application_service.py`](application_service.py) | **`create_application()`** — insert; ValueError on duplicate apply_url. **`get_application()`** — by id; ValueError if not found. **`list_application_urls()`** — all apply_urls for fallback dedup. **`dedup_urls()`** — single .in_() query; returns (new_urls, applied_urls). **`list_applications()`** — paginated by date desc. **`count_applications()`** — total count. **`update_application()`** — patch interview/offer/rejected. **`delete_application()`** — remove by id. |
| [`email_service.py`](email_service.py) | **`scan_inbox()`** — Gmail OAuth2, read-only; classify emails (interview/offer/rejection); match to applications by sender/domain; update flags; return EmailScanResponse. Raises RuntimeError if credentials missing. |
| [`matching_service.py`](matching_service.py) | **`_extract_jd_fields()`** — LLM extraction (skill_set, education_requirement, yoe_required). **`_education_gate()`** — PhD → skip. **`_get_profile_yoe()`** — sum months from work_experiences. **`run_match_pipeline()`** — for job_ids: extract → gates → keyword prefilter → LLM score → store. **`get_recommendations()`** — fully/half matched jobs. **`get_skill_histogram()`** — skill frequencies across jobs. Phase 2+ only (requires ANTHROPIC_API_KEY). |
| [`report_service.py`](report_service.py) | **`generate_report()`** — fetch last 100 applications, build summary, call Claude Sonnet for weekly report. Returns ReportResponse. Raises RuntimeError on failure. Phase 2+ only. |
