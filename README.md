# AI Job Hunting Assistant — Server

Backend service for the AI Job Hunting Assistant. This module implements the **User Professional Profile** API and the **Job Ingestion** pipeline using Python, FastAPI, PostgreSQL, SQLAlchemy 2.0 (async), and Alembic.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI (async) |
| Validation | Pydantic v2 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async style) |
| Migrations | Alembic |
| Driver (async) | asyncpg |
| Driver (sync/migrations) | psycopg2-binary |
| Containerization | Docker Compose |

## Project Structure

```
server/
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── Dockerfile                   # App container image
├── docker-compose.yml           # App + Postgres orchestration
├── .dockerignore                # Docker build exclusions
├── alembic/                     # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_create_user_profile_tables.py
│       ├── 002_add_is_remote_to_work_experiences.py
│       └── 003_create_jobs_table.py
└── app/                         # Application package
    ├── main.py                  # FastAPI entry point
    ├── db/                      # Database infrastructure
    │   ├── base.py
    │   └── session.py
    ├── models/                  # SQLAlchemy ORM models
    │   ├── user.py
    │   ├── education.py
    │   ├── work_experience.py
    │   ├── project.py
    │   ├── skill.py
    │   └── job.py
    ├── schemas/                 # Pydantic request/response schemas
    │   ├── profile.py
    │   └── job_schema.py
    ├── services/                # Business logic layer
    │   ├── profile_service.py
    │   ├── education_service.py
    │   ├── work_experience_service.py
    │   ├── project_service.py
    │   └── job_service.py
    └── routers/                 # FastAPI route handlers
        ├── profile_router.py
        ├── education_router.py
        ├── work_experience_router.py
        ├── project_router.py
        └── job_router.py
```

## Quick Start (Docker)

```bash
docker-compose up --build
```

This starts PostgreSQL and the FastAPI app. Alembic migrations run automatically on boot.

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

## Quick Start (Local)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and edit environment variables
cp .env.example .env

# 3. Create the PostgreSQL database
createdb job_hunting_assistant

# 4. Run migrations
alembic upgrade head

# 5. Start the server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Profiles

| Method | Path | Status | Description |
|---|---|---|---|
| `GET` | `/profiles` | `200` | List all profiles (summary: id + email) |
| `POST` | `/profiles` | `201` | Create a full user profile |
| `GET` | `/profiles/{id}` | `200` | Get profile by ID (nested response) |
| `PUT` | `/profiles/{id}` | `200` | Update profile (replace child lists) |
| `DELETE` | `/profiles/{id}` | `200` | Delete profile (cascade) |

### Educations (nested under profile)

| Method | Path | Status | Description |
|---|---|---|---|
| `GET` | `/profiles/{id}/educations` | `200` | List all educations |
| `POST` | `/profiles/{id}/educations` | `201` | Add an education entry |
| `GET` | `/profiles/{id}/educations/{eid}` | `200` | Get single education |
| `PUT` | `/profiles/{id}/educations/{eid}` | `200` | Update education (partial) |
| `DELETE` | `/profiles/{id}/educations/{eid}` | `200` | Delete education |

### Work Experiences (nested under profile)

| Method | Path | Status | Description |
|---|---|---|---|
| `GET` | `/profiles/{id}/work-experiences` | `200` | List all work experiences |
| `POST` | `/profiles/{id}/work-experiences` | `201` | Add a work experience entry |
| `GET` | `/profiles/{id}/work-experiences/{wid}` | `200` | Get single work experience |
| `PUT` | `/profiles/{id}/work-experiences/{wid}` | `200` | Update work experience (partial) |
| `DELETE` | `/profiles/{id}/work-experiences/{wid}` | `200` | Delete work experience |

### Projects (nested under profile)

| Method | Path | Status | Description |
|---|---|---|---|
| `GET` | `/profiles/{id}/projects` | `200` | List all projects |
| `POST` | `/profiles/{id}/projects` | `201` | Add a project entry |
| `GET` | `/profiles/{id}/projects/{pid}` | `200` | Get single project |
| `PUT` | `/profiles/{id}/projects/{pid}` | `200` | Update project (partial) |
| `DELETE` | `/profiles/{id}/projects/{pid}` | `200` | Delete project |

### Job Ingestion

| Method | Path | Status | Description |
|---|---|---|---|
| `POST` | `/jobs/ingest` | `201` | Ingest a job posting from any external collector |

## Example Postman Request — POST /profiles

```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-416-555-0100",
  "linkedin_url": "https://linkedin.com/in/janedoe",
  "github_url": "https://github.com/janedoe",
  "personal_website": "https://janedoe.dev",
  "location_country": "Canada",
  "location_province_state": "Ontario",
  "location_city": "Toronto",
  "educations": [
    {
      "institution_name": "University of Toronto",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "address_country": "Canada",
      "address_province_state": "Ontario",
      "address_city": "Toronto",
      "start_date": "2018-09",
      "graduate_date": "2022-06",
      "gpa": "3.8",
      "description": "Dean's list, capstone project on NLP"
    }
  ],
  "work_experiences": [
    {
      "company_name": "Google",
      "job_title": "Software Engineer",
      "location_country": "United States",
      "location_province_state": "California",
      "location_city": "Mountain View",
      "start_date": "2022-07",
      "end_date": null,
      "is_remote": false,
      "description": "Full-stack development on Cloud Platform"
    }
  ],
  "projects": [
    {
      "project_title": "AI Job Hunting Assistant",
      "start_date": "2025-01",
      "end_date": null,
      "description": "End-to-end career strategist platform"
    }
  ],
  "skills": [
    { "skill_name": "Python", "skill_category": "language" },
    { "skill_name": "FastAPI", "skill_category": "framework" },
    { "skill_name": "PostgreSQL", "skill_category": "database" }
  ]
}
```

## Example Postman Request — POST /jobs/ingest

```json
{
  "website": "linkedin",
  "job_title": "Software Engineer",
  "company": "Google",
  "location": "Vancouver, BC",
  "job_description": "Full original job content here...",
  "post_datetime": "2026-02-27T10:00:00Z",
  "source_url": "https://linkedin.com/job/123",
  "search_keyword": "Software Engineer",
  "search_location": "Vancouver"
}
```

## Database Schema (ER Diagram)

```
┌──────────────┐
│    users     │
│──────────────│
│ id (PK, UUID)│        ┌────────────────────┐
│ name         │───1:N──│    educations       │
│ email (UQ)   │        │────────────────────│
│ phone        │        │ id (PK)            │
│ linkedin_url │        │ user_id (FK)       │
│ github_url   │        │ institution_name   │
│ personal_web │        │ degree             │
│ location_*   │        │ field_of_study     │
│ created_at   │        │ address_*          │
│ updated_at   │        │ start_date         │
│              │        │ graduate_date      │
│              │        │ gpa                │
│              │        │ description        │
│              │        │ created_at         │
│              │        └────────────────────┘
│              │
│              │        ┌────────────────────┐
│              │───1:N──│  work_experiences   │
│              │        │────────────────────│
│              │        │ id (PK)            │
│              │        │ user_id (FK)       │
│              │        │ company_name       │
│              │        │ job_title          │
│              │        │ location_*         │
│              │        │ start_date         │
│              │        │ end_date           │
│              │        │ is_remote          │
│              │        │ description        │
│              │        │ created_at         │
│              │        └────────────────────┘
│              │
│              │        ┌────────────────────┐
│              │───1:N──│     projects        │
│              │        │────────────────────│
│              │        │ id (PK)            │
│              │        │ user_id (FK)       │
│              │        │ project_title      │
│              │        │ start_date         │
│              │        │ end_date           │
│              │        │ description        │
│              │        │ created_at         │
│              │        └────────────────────┘
│              │
│              │        ┌────────────────────┐
│              │───1:N──│      skills         │
│              │        │────────────────────│
│              │        │ id (PK)            │
│              │        │ user_id (FK)       │
│              │        │ skill_name         │
│              │        │ skill_category     │
│              │        │ created_at         │
└──────────────┘        └────────────────────┘


┌──────────────────────┐
│    jobs (standalone)  │
│──────────────────────│
│ id (PK, UUID)        │
│ website              │  ← "linkedin", "indeed", "glassdoor"
│ job_title            │
│ company              │
│ location             │
│ job_description      │
│ post_datetime        │
│ source_url (UQ*)     │  ← partial unique where NOT NULL
│ search_keyword       │
│ search_location      │
│ created_at           │
│──────────────────────│
│ ix: website          │
│ ix: job_title        │
│ ix: company          │
│ ix: dedup (website,  │
│     job_title,       │
│     company)         │
└──────────────────────┘
```

## Files in This Directory

| File | Description |
|---|---|
| [`alembic.ini`](alembic.ini) | Alembic configuration file. Defines the migration script location, the default database URL, and logging settings. |
| [`requirements.txt`](requirements.txt) | Python dependency list — FastAPI, uvicorn, Pydantic (with email validation), SQLAlchemy, asyncpg, Alembic, psycopg2-binary, python-dotenv. |
| [`.env.example`](.env.example) | Template for environment variables. Contains `DATABASE_URL` (async) and `DATABASE_URL_SYNC` (sync for Alembic). |
| [`Dockerfile`](Dockerfile) | Builds the app container image. Runs Alembic migrations on startup then launches uvicorn. |
| [`docker-compose.yml`](docker-compose.yml) | Orchestrates the FastAPI app and PostgreSQL 16 services. Postgres health-checked before app starts. |
| [`.dockerignore`](.dockerignore) | Excludes unnecessary files from Docker build context. |

## Subdirectories

| Directory | Description |
|---|---|
| [`alembic/`](alembic/README.md) | Database migration scripts and Alembic runtime configuration. |
| [`app/`](app/README.md) | Main application package — API routes, services, schemas, models, and database infrastructure. |
