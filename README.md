# AI Job Hunting Assistant — Server

Backend service for the AI Job Hunting Assistant. This module implements the **User Professional Profile** schema using Python, PostgreSQL, SQLAlchemy 2.0 (async), and Alembic.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 (async style) |
| Migrations | Alembic |
| Driver (async) | asyncpg |
| Driver (sync/migrations) | psycopg2-binary |

## Project Structure

```
server/
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── alembic/                     # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_create_user_profile_tables.py
└── app/                         # Application package
    ├── db/                      # Database infrastructure
    │   ├── base.py
    │   └── session.py
    └── models/                  # SQLAlchemy ORM models
        ├── user.py
        ├── education.py
        ├── work_experience.py
        └── skill.py
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and edit environment variables
cp .env.example .env

# 3. Create the PostgreSQL database
createdb job_hunting_assistant

# 4. Run migrations
alembic upgrade head
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
│ created_at   │        │ start_date         │
│ updated_at   │        │ graduate_date      │
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
│              │        │ proficiency_level  │
│              │        │ created_at         │
└──────────────┘        └────────────────────┘
```

## Files in This Directory

| File | Description |
|---|---|
| [`alembic.ini`](alembic.ini) | Alembic configuration file. Defines the migration script location, the default database URL (`postgresql+psycopg2://...`), and logging settings for Alembic and SQLAlchemy. |
| [`requirements.txt`](requirements.txt) | Python dependency list. Pins minimum versions for `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `psycopg2-binary`, and `python-dotenv`. |
| [`.env.example`](.env.example) | Template for environment variables. Contains `DATABASE_URL` (async, for the app) and `DATABASE_URL_SYNC` (sync, for Alembic migrations). Copy to `.env` and fill in real credentials. |

## Subdirectories

| Directory | Description |
|---|---|
| [`alembic/`](alembic/README.md) | Database migration scripts and Alembic runtime configuration. |
| [`app/`](app/README.md) | Main application package containing database infrastructure and ORM models. |
