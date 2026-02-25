# alembic/

Database migration management powered by [Alembic](https://alembic.sqlalchemy.org/).

---

**Navigation:** [< Back to Root](../README.md) | **Sibling:** [app/](../app/README.md)

---

## Purpose

This directory contains everything Alembic needs to generate, store, and execute database migrations against PostgreSQL. Migrations are version-controlled Python scripts that evolve the schema incrementally.

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package marker. Empty file that allows Python to treat this directory as a module. |
| [`env.py`](env.py) | Alembic runtime environment. Loads the SQLAlchemy `Base.metadata` from `app.db.base` and imports all models (`User`, `Education`, `WorkExperience`, `Skill`) so autogenerate can detect schema changes. Reads `DATABASE_URL_SYNC` from `.env` to override the default connection string. Supports both **offline** (SQL script generation) and **online** (direct database connection) migration modes. |
| [`script.py.mako`](script.py.mako) | Mako template used by `alembic revision --autogenerate` to generate new migration files. Defines the boilerplate structure: revision ID, dependency chain, and `upgrade()`/`downgrade()` function stubs. |

## Subdirectories

| Directory | Description |
|---|---|
| [`versions/`](versions/README.md) | Contains all migration revision scripts, ordered chronologically. |

## Common Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# Auto-generate a new migration from model changes
alembic revision --autogenerate -m "describe your change"

# Show current migration state
alembic current

# View migration history
alembic history
```
