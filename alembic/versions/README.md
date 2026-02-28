# alembic/versions/

Individual database migration revision scripts.

---

**Navigation:** [< Back to alembic/](../README.md) | [<< Back to Root](../../README.md)

---

## Purpose

Each file in this directory represents a single migration revision. Revisions form a linked chain — each one knows its predecessor (`down_revision`) so Alembic can apply or rollback them in order.

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package marker. Empty file. |
| [`001_create_user_profile_tables.py`](001_create_user_profile_tables.py) | **Initial migration.** Creates the full User Professional Profile schema: `users`, `educations`, `work_experiences`, `projects`, and `skills` tables. Also creates the `skill_category_enum` PostgreSQL ENUM type. Defines all primary keys (UUID), foreign keys (`ON DELETE CASCADE`), unique constraints (`email`), check constraints (`graduate_date >= start_date`, `end_date >= start_date`), and indexes (`email`, `user_id`, `company_name`, `skill_name`). The `downgrade()` drops all five tables and the enum in reverse order. |
| [`002_add_is_remote_to_work_experiences.py`](002_add_is_remote_to_work_experiences.py) | Adds `is_remote` Boolean column to `work_experiences` table with a server default of `false`. |
| [`003_create_jobs_table.py`](003_create_jobs_table.py) | Creates the standalone `jobs` table for external job posting ingestion. Columns: `website`, `job_title`, `company`, `location`, `job_description`, `post_datetime`, `source_url`, `search_keyword`, `search_location`, `created_at`. Indexes: `website`, `job_title`, `company`, partial unique on `source_url` (where NOT NULL), composite dedup `(website, job_title, company)`. |

## Revision Chain

```
(base) ──> 001_create_user_profile_tables ──> 002_add_is_remote ──> 003_create_jobs_table
```

## Adding New Migrations

After modifying models in `app/models/`, generate a new revision:

```bash
alembic revision --autogenerate -m "describe your change"
```

The new file will appear here with the next revision ID, linked to `003` as its `down_revision`.
