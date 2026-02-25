# app/db/

Database infrastructure layer.

---

**Navigation:** [< Back to app/](../README.md) | [<< Back to Root](../../README.md) | **Sibling:** [models/](../models/README.md)

---

## Purpose

This package provides the foundational database components that all models and services depend on: the SQLAlchemy declarative base class and the async database session management.

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package marker. Empty file. |
| [`base.py`](base.py) | Defines `Base`, the SQLAlchemy `DeclarativeBase` that all ORM models inherit from. Key features: **(1)** Attaches a `MetaData` with a consistent naming convention for all constraints (`ix_`, `uq_`, `ck_`, `fk_`, `pk_` prefixes) to ensure deterministic, Alembic-friendly constraint names. **(2)** Declares shared columns inherited by every model: `id` (UUID primary key, auto-generated via `uuid.uuid4`) and `created_at` (timezone-aware timestamp, defaults to UTC now). |
| [`session.py`](session.py) | Configures the async database connection. Reads `DATABASE_URL` from environment variables (falling back to a localhost default). Creates an `AsyncEngine` via `create_async_engine` (asyncpg driver) and an `async_sessionmaker` factory. Exposes `get_session()`, an async generator that yields `AsyncSession` instances — designed to be used as a FastAPI dependency or in any async context. |
