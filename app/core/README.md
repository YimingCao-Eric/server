# app/core/

Configuration and settings for the AI Job Hunting Assistant backend.

---

## Project Idea (from [overview.md](../../overview.md))

Centralized config for the 24/7 job hunting backend: database URLs, scraper webhooks, Gmail OAuth2 (for email monitoring), and Anthropic API key (Phase 2+).

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../ (app)](../README.md) |
| **Next folder** | [../db/](db/README.md) |
| **Siblings** | [models/](../models/README.md) · [schemas/](../schemas/README.md) · [services/](../services/README.md) · [routers/](../routers/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`__init__.py`](__init__.py) | Package marker. Empty; makes `app.core` importable. |
| [`config.py`](config.py) | **Settings class** — `pydantic_settings.BaseSettings` loads from `.env`. **Attributes:** `database_url` (asyncpg), `database_url_sync` (psycopg2 for Alembic), `backend_base_url` (self-reference for ingest callback), `scraper_webhook_linkedin` / `_indeed` / `_glassdoor` (Phase 2/3 webhook URLs), `anthropic_api_key` (Phase 2+ backend LLM), `gmail_client_id`, `gmail_client_secret`, `gmail_refresh_token` (Gmail OAuth2 for `POST /email/scan`). Exposes `settings = Settings()`. |
