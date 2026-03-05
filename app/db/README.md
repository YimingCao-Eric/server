# app/db/

Database infrastructure layer.

---

## Project Idea (from [overview.md](../../overview.md))

Provides the SQLAlchemy declarative base and async session management used by all models and services. The backend uses PostgreSQL 16 with asyncpg for low-latency, non-blocking DB access.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../core/](core/README.md) |
| **Next folder** | [../models/](models/README.md) |
| **Siblings** | [schemas/](../schemas/README.md) · [services/](../services/README.md) · [routers/](../routers/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`base.py`](base.py) | **`Base`** — SQLAlchemy `DeclarativeBase` that all ORM models inherit from. **Features:** (1) `MetaData` with naming convention (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`) for deterministic constraint names. (2) Shared columns: `id` (UUID, `uuid.uuid4`), `created_at` (timezone-aware, UTC). **Class:** `Base`. |
| [`session.py`](session.py) | **Async database connection.** Reads `DATABASE_URL` from config. **Functions:** `get_session()` — async generator yielding `AsyncSession`; use as FastAPI dependency. **Objects:** `engine` (create_async_engine), `async_session_factory` (async_sessionmaker). |
