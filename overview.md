# AI Job Hunting Assistant — Project Overview
> Eric (Yiming Cao) | Started Jan 2026
> GitHub: https://github.com/YimingCao-Eric/server
> Last updated: 2026-03-04

---

## What This Is

A fully automated job hunting system that runs 24/7 on a dedicated machine.
It searches LinkedIn daily, scores job postings against Eric's profile using LLM
matching, tracks applications, monitors email for interview/offer/rejection signals,
and generates weekly strategy reports — with zero manual browsing required.

The system is designed in three progressive phases. The backend never changes
between phases. Only the scraper layer evolves.

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    STABLE CORE (all phases)                  │
│                                                              │
│  FastAPI Backend (Python)      PostgreSQL 16                 │
│  ┌─ Ingest & scrape           ┌─ jobs                        │
│  ├─ Match & recommend         ├─ job_applications            │
│  ├─ Application tracking      ├─ users / educations /        │
│  ├─ Email scanning            │  work_experiences /          │
│  └─ Report storage            │  projects / skills           │
│                               └─────────────────────────────│
└────────────────────────┬────────────────────────────────────┘
                         │ API calls
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐    ┌──────────────┐
    │ Phase 1 │    │ Phase 2  │    │   Phase 3    │
    │OpenClaw │    │   n8n    │    │   Python     │
    │ Direct  │    │Workflows │    │  Scraper     │
    │ (NOW)   │    │(PLANNED) │    │  (FUTURE)    │
    └─────────┘    └──────────┘    └──────────────┘
```

Phase transitions require two config changes: set `SCRAPER_WEBHOOK_LINKEDIN` in
backend `.env`, and set `SCRAPE_MODE=webhook` in OpenClaw's `MEMORY.md`.
Backend code: zero change across all phases.

---

## The 6-Step Pipeline

The same pipeline runs in all three phases.

```
Step 1  SEARCH          Scrape one LinkedIn page (25 jobs) per hourly run
Step 2  URL DEDUP       Filter out jobs already applied to
Step 3  MATCH           Extract JD fields → gate → LLM skill score → recommend
Step 4  APPLY CONFIRM   Eric confirms → log to job_applications
Step 5  EMAIL MONITOR   Scan Gmail → detect interview/offer/rejection → alert
Step 6  WEEKLY REPORT   LLM analysis of full application history → Monday 08:00
```

---

## Phase 1 — Complete ✅

### What It Is

OpenClaw (Claude's agentic interface) runs on a dedicated 24/7 machine.
It is the scraper, the LLM engine, and the orchestrator — all in one.
No external infrastructure. No Anthropic API key needed.
The FastAPI backend is pure storage and retrieval.

### How It Works End-to-End

```
Every hour 08:00–20:00:

  [Step 1 — Search]
  OpenClaw fetches one LinkedIn page:
    linkedin.com/jobs/search?keywords=software+engineer
      &location=Canada&f_TPR=r86400&start={(page-1)*25}
  For each job found → POST /jobs/ingest
    Request:  {website, job_title, company, location, job_description,
               source_url, post_datetime, search_keyword, search_location}
    Response: {id, already_exists}
  Increments CURRENT_PAGE in MEMORY.md

  [Step 2 — URL Dedup]
  POST /jobs/applications/dedup {urls: [25 scraped source_urls]}
  → Returns: {new_urls, already_applied, total_input, new_count, applied_count}
  → Only new_urls are passed to Step 3
  → Already-applied jobs silently discarded

  [Step 3 — Match + Recommend]
  GET /profiles/{id}/resume-text  (≤500 tokens)
  For each new job, in batches of 5:
    LLM call 1: extract skill_set, education_requirement, yoe_required
    Education gate: PhD required → skip
    YOE gate: (yoe_required - profile_yoe) > 1 → skip
    Keyword prefilter: zero skill overlap → skip
    LLM call 2: score match_level + match_reason
  POST /jobs/match-results per job (stores on jobs row)
  GET /jobs/recommendations/{profile_id}
  GET /jobs/skill-histogram
  If fully/half matched jobs exist → send to Eric

  [Step 4 — Apply Confirm]
  Eric replies confirming which jobs he applied to
  POST /jobs/applications per confirmed job
  Important: apply_url must equal the job's source_url — this is the key
  that dedup (Step 2) checks against. Using any other URL breaks dedup.

Every hour 08:00–20:00:

  [Step 5 — Email Monitor]
  POST /email/scan (Gmail OAuth2, read-only)
  Offer      → immediate alert → PUT flag
  Interview  → backend classifies + sets flag → OpenClaw reads event → LLM generates prep plan → immediate alert
  Rejection  → silent log → Monday report
  No match   → log as unmatched

Every Monday 08:00:

  [Step 6 — Weekly Report]
  GET /jobs/applications?limit=100 (paginated)
  LLM generates report: applications, interviews, rejections,
    offers, skill gaps, recommended focus
  POST /reports/store  (stored in-memory — lost on server restart; Phase 2 will persist to DB)
  Send report to Eric
```

### Database Tables

| Table | Purpose | Grows when |
|-------|---------|------------|
| `jobs` | All scraped jobs — market intelligence + match cache | Every LinkedIn page fetch |
| `job_applications` | Jobs Eric confirmed applying to | Eric confirms in Step 4 |
| `users` | Eric's profile | Manual setup |
| `educations` | Degree records | Manual setup |
| `work_experiences` | Job history | Manual setup |
| `projects` | Project records | Manual setup |
| `skills` | Skill list | Manual setup |

### Migrations

| # | File | Contents |
|---|------|----------|
| 001 | `001_create_user_profile_tables.py` | `users`, `educations`, `work_experiences`, `projects`, `skills` |
| 002 | `002_add_is_remote_to_work_experiences.py` | `is_remote` on `work_experiences` |
| 003 | `003_create_jobs_table.py` | `jobs` table with dedup indexes |
| 004 | `004_add_updated_at_to_jobs.py` | `updated_at` on `jobs` |
| 005 | `005_add_matching_columns_to_jobs.py` | Matching columns on `jobs`: `match_level`, `match_reason`, `matched_at`, `is_active`, `extracted_yoe`, `extracted_skills`, `extracted_education` (Text — fixed in 009), `raw_description_hash` |
| 006 | `006_create_job_applications_table.py` | `job_applications` table |
| 007 | `007_create_job_hunt_sessions_table.py` | `job_hunt_sessions` table (created) |
| 008 | `008_remove_job_hunt_sessions.py` | Drop `job_hunt_sessions` (premature — removed) |
| 009 | `009_fix_extracted_education_type.py` | Fix `extracted_education` column type: `Text` → `VARCHAR(20)` |

Note: Gmail OAuth2 credentials (`gmail_client_id`, `gmail_client_secret`, `gmail_refresh_token`) are environment variables in `config.py` — not a DB migration.

### Live Endpoints

**Ingest & Scrape**
```
POST /jobs/ingest               Store one scraped job (deduplicates by source_url) → 200 always
                                  Returns {id, already_exists}. 200 is intentional — same endpoint
                                  handles new and duplicate jobs; 201 would misrepresent duplicates.
POST /jobs/scrape               Webhook trigger (unused in Phase 1)
```

**Matching**
```
POST /jobs/match                Backend LLM pipeline (Phase 2/3 only)
POST /jobs/match-results        OpenClaw pushes pre-computed match data (Phase 1)
GET  /jobs/recommendations/{id} Return fully/half matched jobs
GET  /jobs/skill-histogram      Skill frequencies across all scraped jobs
GET  /profiles/{id}/resume-text Condensed resume text + token_estimate (OpenClaw uses ≤500 tokens of this)
```

**Application Tracking**
```
POST /jobs/applications              Log a confirmed application
GET  /jobs/applications              List applications (paginated ?limit=&offset=)
GET  /jobs/applications/count        Total count (no records loaded)
GET  /jobs/applications/urls         All apply_urls only (fallback dedup)
POST /jobs/applications/dedup        Server-side URL dedup — primary method
GET  /jobs/applications/{id}         Single application
PUT  /jobs/applications/{id}         Update flags (interview/offer/rejected)
```

**Email & Reports**
```
POST /email/scan         Scan Gmail inbox, classify, update flags
POST /reports/generate   Backend LLM report (Phase 2/3 only)
POST /reports/store      OpenClaw pushes pre-written report (Phase 1)
                           Body: {report_text: str, applications_analysed?: int (default 0)}
                           Stored in-memory — lost on server restart
GET  /reports/latest     Retrieve most recent report
```

**Diagnostics**
```
GET  /health                    Returns {status: "ok"} — used for container health checks
```

**Profile CRUD**
```
Full CRUD on: profiles, educations, work_experiences, projects, skills
Base path: /profiles
Nested: /profiles/{id}/educations
        /profiles/{id}/work-experiences
        /profiles/{id}/projects
        /profiles/{id}/skills
```

### Key Design Decisions

**LLM in OpenClaw, not backend (Phase 1)**
All extraction and matching happens inside OpenClaw using Eric's Claude Pro plan.
The backend has no Anthropic API key and makes no LLM calls.
`POST /jobs/match-results` and `POST /reports/store` are the write-back endpoints.
In Phase 2, the backend activates its own LLM path for the scheduled headless mode.

**Pagination-by-run (one LinkedIn page per hourly run)**
Simulates human browsing. MEMORY.md tracks `CURRENT_PAGE` and `SEARCH_EXHAUSTED`.
URL dedup handles overlap between pages automatically.
12 runs/day × 25 jobs = up to 300 jobs/day coverage.

**Two-table separation**
`jobs` = market intelligence scratchpad. All scraped jobs land here including
irrelevant ones. Powers skill histogram and report market context.
`job_applications` = Eric's actual application history. Only grows when he confirms.

**Server-side dedup at O(1)**
`POST /jobs/applications/dedup` takes today's 25 URLs, does a single `.in_()` query,
returns only the new ones. Token cost is constant regardless of application history size.

Dedup contract: `job_applications.apply_url` must equal `jobs.source_url` for the
same posting. OpenClaw enforces this in Step 4 — `apply_url` is always copied from
the job's `source_url`, never from a redirect or alternate URL.

**Matching pipeline gates before LLM**
Education gate → YOE gate → keyword prefilter run CPU-only before any LLM call.
Only jobs that pass all three gates reach the LLM skill scorer.
Reduces LLM calls by an estimated 40–60% of raw scraped volume.

### MEMORY.md State Machine

```
CURRENT_SEARCH_KEYWORD: software engineer
CURRENT_SEARCH_LOCATION: Canada
CURRENT_PAGE: 1                  ← increments each run
CURRENT_SEARCH_DATE: 2026-03-04  ← reset triggers page=1
SEARCH_EXHAUSTED: false          ← true when page returns 0 results
TODAY_SEARCHES: 0                ← total runs today
```

### OpenClaw Config Files

| File | Purpose |
|------|---------|
| `AGENTS.md` v5 | Full pipeline logic, endpoint registry, batching rules, error handling |
| `MEMORY.md` | Persistent state between hourly runs |
| `SOUL.md` v3 | Tone, values, operating philosophy |
| `USER.md` v3 | Eric's full resume, target roles, preferences |

---

## Phase 2 — Planned (n8n)

**What changes:** OpenClaw calls `POST /jobs/scrape` instead of scraping directly.
The backend fires a webhook to n8n. n8n searches LinkedIn/Indeed/Glassdoor and
calls back `POST /jobs/ingest` per job. OpenClaw waits 60 seconds then runs
Steps 2–6 identically.

**What stays the same:** Everything. Backend code, DB schema, all endpoints,
all OpenClaw logic from Step 2 onward.

**New capability:** Headless scheduled mode. APScheduler in the scraper service
fires at scheduled times without OpenClaw needing to be the trigger.
Two modes coexist:
- Scheduled (headless): n8n scrapes → backend LLM via `matching_service.py`
- User-initiated: Eric tells OpenClaw → OpenClaw LLM as in Phase 1

**Transition:** Set `SCRAPER_WEBHOOK_LINKEDIN` env var in backend `.env` + set `SCRAPE_MODE=webhook` in OpenClaw's `MEMORY.md`.

Note: `SCRAPE_MODE` is an OpenClaw orchestration flag stored in `MEMORY.md` — it is not a backend environment variable. The backend does not read it.

**Phase 2 backend additions planned:**
- `POST /jobs/cleanup` — deactivate stale irrelevant jobs older than 30 days
- Migration 010 — composite index on `jobs(match_level, post_datetime DESC) WHERE is_active=true`
- Session analytics (design pending before implementation)
- `asyncio.gather()` concurrency in `matching_service.py`

---

## Phase 3 — Future (Python Scraper Microservice)

**What changes:** A dedicated `scraper/` FastAPI microservice replaces n8n.
Same webhook interface — `SCRAPER_WEBHOOK_*` env vars point to it.
jobspy + playwright for scraping. APScheduler built in. Docker-native.

**What stays the same:** Everything in the backend. Zero code changes.

**New capability:** Full code control, proxy rotation, multi-user ready,
production-grade scheduling, Playwright stealth mode.

**Transition:** Add `scraper/` to `docker-compose.yml`, update `SCRAPER_WEBHOOK_*`
to point at the microservice.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 |
| Database | PostgreSQL 16, asyncpg, Alembic migrations |
| HTTP client | httpx async |
| Config | pydantic-settings, .env |
| Email | Gmail API, google-auth OAuth2 |
| LLM (Phase 1) | Claude Pro via OpenClaw (no API key) |
| LLM (Phase 2+) | Anthropic API — claude-haiku (extraction), claude-sonnet (report) |
| Scraper (Phase 1) | OpenClaw web search |
| Scraper (Phase 2) | n8n workflows |
| Scraper (Phase 3) | jobspy, Playwright |
| Orchestration | Docker, docker-compose |
| Agent interface | OpenClaw (all phases) |

---

## Optimizations Completed

| # | Optimization | Impact |
|---|-------------|--------|
| Fix 1 | `GET /jobs/applications/urls` | 97% token reduction for URL list fetches |
| Fix 2 | `POST /jobs/applications/dedup` | O(1) dedup regardless of history size |
| Fix 3 | Pagination on `GET /jobs/applications` | Unbounded list protected |
| Fix 4 | `GET /jobs/applications/count` | Stats without loading records |
| 1B | Batched JD extraction (5 per LLM call) | 5× latency reduction in Step 3 |
| 3C/4D | Removed `job_hunt_sessions` | Premature table eliminated |

## Optimizations Planned

| # | Optimization | Phase |
|---|-------------|-------|
| 1A | Skip static file re-reads in session start | Phase 2 |
| 2A | `asyncio.gather()` in backend matching | Phase 2 |
| 3A | Composite index on jobs table | Phase 2 |
| 5A | Read last 5 log entries only | Phase 2 |
| 3B | Stale job cleanup | Deferred |
| 2C | Gmail batch API | Phase 3 |
| 1F | `/jobs/applications/summary` endpoint | Phase 3 |

---

## Current Status

**Phase 1: Complete and ready to run live.**

All backend endpoints built and smoke-tested.
AGENTS.md v5 and MEMORY.md written.
Load config files into OpenClaw on the 24/7 machine to activate.

**Next:** Phase 2 planning.