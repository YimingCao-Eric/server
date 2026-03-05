# alembic/

Database migration management powered by [Alembic](https://alembic.sqlalchemy.org/).

---

## Project Idea (from [overview.md](../overview.md))

Migrations evolve the PostgreSQL schema incrementally. The backend uses migrations 001–009 to create and evolve tables: users, educations, work_experiences, projects, skills, jobs, job_applications. The backend never changes between phases; schema stays stable.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../ (Root)](../README.md) |
| **Next folder** | [versions/](versions/README.md) |
| **Sibling** | [app/](../app/README.md) · [scripts/](../scripts/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`env.py`](env.py) | **Alembic runtime environment.** Loads `Base.metadata` from `app.db.base`; imports all models (User, Education, WorkExperience, Project, Skill, Job, JobApplication) so autogenerate detects schema. Reads `DATABASE_URL_SYNC` from `.env`. **Functions:** `run_migrations_offline()` — generates SQL script; `run_migrations_online()` — connects to DB and runs migrations. |
| [`script.py.mako`](script.py.mako) | Mako template for `alembic revision --autogenerate`. Boilerplate: revision ID, `down_revision`, `upgrade()`, `downgrade()`. |

---

## Subdirectories

| Directory | Description |
|-----------|--------------|
| [**versions/**](versions/README.md) | Migration revision scripts 001–009. |

---

## Common Commands

```bash
alembic upgrade head       # Apply all pending migrations
alembic downgrade -1       # Rollback last migration
alembic revision --autogenerate -m "describe change"  # Generate new migration
alembic current            # Show current revision
alembic history            # View migration history
```
