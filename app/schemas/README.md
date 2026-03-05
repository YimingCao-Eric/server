# app/schemas/

Pydantic schemas for request validation and response serialization.

---

## Project Idea (from [overview.md](../../overview.md))

Schemas validate incoming JSON and serialize SQLAlchemy model instances for API responses. They enforce the 6-step pipeline contract: ingest requests, dedup requests/responses, application create/update, email scan response, report store/response.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../models/](models/README.md) |
| **Next folder** | [../routers/](routers/README.md) |
| **Siblings** | [core/](../core/README.md) · [db/](../db/README.md) · [services/](../services/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`__init__.py`](__init__.py) | Re-exports profile schemas: `EducationCreate`/`Update`/`Response`, `WorkExperienceCreate`/`Update`/`Response`, `ProjectCreate`/`Update`/`Response`, `SkillCreate`/`Response`, `ProfileCreate`/`Update`/`SummaryResponse`/`Response`. |
| [`profile.py`](profile.py) | Profile CRUD schemas. **Create:** `EducationCreate`, `WorkExperienceCreate`, `ProjectCreate`, `SkillCreate`, `ProfileCreate` — dates accept `YYYY-MM` or `YYYY-MM-DD`; cross-field validators for `graduate_date >= start_date`, `end_date >= start_date`; `skill_category` enum; `is_remote` default false. **Update:** `*Update` schemas with optional fields. **Response:** `*Response`, `ProfileSummaryResponse` (id + email only). |
| [`job_schema.py`](job_schema.py) | **Ingest:** `JobIngestRequest` (website, job_title, company, location, job_description, post_datetime, source_url, search_keyword, search_location) — strips whitespace, rejects empty required fields. `JobIngestResponse` (id, already_exists). **Match:** `JobMatchResultWrite`, `JobMatchResultResponse`, `JobMatchRequest`, `JobMatchResponse`, `JobMatchResult`, `JobRecommendation`, `SkillHistogramItem`. |
| [`job_scrape_schema.py`](job_scrape_schema.py) | **Scrape trigger:** `ScrapeRequest` (website, job_title, location, date_posted_filter, max_results). `ScrapeResponse` (message, website, status). |
| [`application_schema.py`](application_schema.py) | **Application:** `JobApplicationCreate` (job_title, company_name, apply_url, date_year/month/day, job_description, yoe, skill_set). `JobApplicationUpdate` (interview, offer, rejected — optional booleans). `JobApplicationRead` (full application with from_attributes). **Dedup:** `DedupRequest` (urls: list[str]). `DedupResponse` (new_urls, already_applied, total_input, new_count, applied_count). `ApplicationCountResponse` (count). |
| [`email_schema.py`](email_schema.py) | **Email scan:** `EmailEventType` enum (interview_invite, rejection, offer, unmatched). `EmailEvent` (event_type, sender, subject, application_id, company_name, updated_flag). `EmailScanResponse` (events, total_scanned, interview_count, rejection_count, offer_count, unmatched_count). |
| [`report_schema.py`](report_schema.py) | **Report:** `ReportStoreRequest` (report_text, applications_analysed=0). `ReportResponse` (report_text, applications_analysed, generated_at). |
