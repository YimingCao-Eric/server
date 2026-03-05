# AI Job Hunting Assistant — Server

Backend service for a fully automated job hunting system. See [overview.md](overview.md) for the full project vision and architecture.

---

## Project Idea (from [overview.md](overview.md))

A fully automated job hunting system that runs 24/7 on a dedicated machine. It searches LinkedIn daily, scores job postings against Eric's profile using LLM matching, tracks applications, monitors email for interview/offer/rejection signals, and generates weekly strategy reports — **with zero manual browsing required**.

The system is designed in three progressive phases. **The backend never changes between phases.** Only the scraper layer evolves.

### The 6-Step Pipeline

| Step | Name           | Description                                                  |
|------|----------------|--------------------------------------------------------------|
| 1    | SEARCH         | Scrape one LinkedIn page (25 jobs) per hourly run             |
| 2    | URL DEDUP      | Filter out jobs already applied to                           |
| 3    | MATCH          | Extract JD fields → gate → LLM skill score → recommend       |
| 4    | APPLY CONFIRM  | Eric confirms → log to `job_applications`                     |
| 5    | EMAIL MONITOR  | Scan Gmail → detect interview/offer/rejection → alert         |
| 6    | WEEKLY REPORT  | LLM analysis of full application history → Monday 08:00      |

### Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    STABLE CORE (all phases)                  │
│  FastAPI Backend      PostgreSQL 16                          │
│  ┌─ Ingest & scrape   ┌─ jobs, job_applications              │
│  ├─ Match & recommend ├─ users, educations, work_experiences│
│  ├─ Application tracking │ projects, skills                  │
│  ├─ Email scanning   └─────────────────────────────────────│
│  └─ Report storage                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Navigation

| Direction | Link |
|-----------|------|
| **Next folder** | [app/](app/README.md) — Main application package |
| **Sibling** | [alembic/](alembic/README.md) — Database migrations |
| **Sibling** | [scripts/](scripts/README.md) — Test scripts |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, Pydantic v2 |
| Database | PostgreSQL 16, asyncpg, Alembic migrations |
| HTTP client | httpx async |
| Config | pydantic-settings, .env |
| Email | Gmail API, google-auth OAuth2 |
| Orchestration | Docker, docker-compose |

---

## Project Structure

```
server/
├── app/                    # Application package
│   ├── core/               # Config and settings
│   ├── db/                 # Database infrastructure
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── services/           # Business logic layer
│   └── routers/            # FastAPI route handlers
├── alembic/                # Database migrations
│   └── versions/           # Migration scripts (001–009)
├── scripts/                # Smoke tests and utilities
├── overview.md             # Full project overview
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
├── Dockerfile              # App container image
└── docker-compose.yml      # App + Postgres orchestration
```

---

## Quick Start (Docker)

```bash
docker-compose up --build
```

- **API:** http://localhost:8000  
- **Swagger UI:** http://localhost:8000/docs  
- **Health check:** http://localhost:8000/health  

---

## Quick Start (Local)

```bash
pip install -r requirements.txt
cp .env.example .env
createdb job_hunting_assistant
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

---

## Root-Level Files

| File | Description |
|------|-------------|
| [`overview.md`](overview.md) | Full project overview: architecture, pipeline, phases, endpoints, design decisions. |
| [`overview_conflicts.md`](overview_conflicts.md) | Comparison of overview vs. codebase; lists discrepancies. |
| [`alembic.ini`](alembic.ini) | Alembic configuration: migration script location, database URL, logging. |
| [`requirements.txt`](requirements.txt) | Python dependencies: FastAPI, SQLAlchemy, Pydantic, asyncpg, Alembic, httpx, etc. |
| [`.env.example`](.env.example) | Template for `.env`: `DATABASE_URL`, scraper webhooks, Gmail OAuth2, `BACKEND_BASE_URL`. |
| [`Dockerfile`](Dockerfile) | Builds app container; runs migrations on startup, then uvicorn. |
| [`docker-compose.yml`](docker-compose.yml) | Orchestrates FastAPI app and PostgreSQL 16. |
| [`.dockerignore`](.dockerignore) | Excludes files from Docker build context. |

---

## Subdirectories

| Directory | Description |
|-----------|--------------|
| [**app/**](app/README.md) | Main application package — routes, services, schemas, models, DB infra. |
| [**alembic/**](alembic/README.md) | Database migration management and revision scripts. |
| [**scripts/**](scripts/README.md) | Smoke tests (Phase 1B/1C/1D), dedup optimization, match/report store. |
