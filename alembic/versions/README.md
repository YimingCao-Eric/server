# alembic/versions/

Individual database migration revision scripts.

---

## Project Idea (from [overview.md](../../overview.md))

Each file is a single migration. Revisions form a linked chain (`down_revision`). Migrations create and evolve the schema for the 6-step pipeline: users/profile tables, jobs, job_applications, matching columns.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../ (alembic)](../README.md) |
| **Next folder** | [../../ (Root)](../../README.md) — *versions is leaf* |
| **Siblings** | None (leaf directory) |

---

## Files

| File | Description |
|------|-------------|
| [`001_create_user_profile_tables.py`](001_create_user_profile_tables.py) | Creates `users`, `educations`, `work_experiences`, `projects`, `skills`, `skill_category_enum`. PKs, FKs (CASCADE), unique email, check constraints. |
| [`002_add_is_remote_to_work_experiences.py`](002_add_is_remote_to_work_experiences.py) | Adds `is_remote` Boolean to `work_experiences`, default false. |
| [`003_create_jobs_table.py`](003_create_jobs_table.py) | Creates `jobs` table: website, job_title, company, location, job_description, post_datetime, source_url, search_keyword, search_location, created_at. Indexes: website, job_title, company, source_url (partial unique), dedup composite. |
| [`004_add_updated_at_to_jobs.py`](004_add_updated_at_to_jobs.py) | Adds `updated_at` DateTime to `jobs`. |
| [`005_add_matching_columns_to_jobs.py`](005_add_matching_columns_to_jobs.py) | Adds match_level, match_reason, matched_at, is_active, extracted_yoe, extracted_skills, extracted_education (Text), raw_description_hash. Indexes on match_level, raw_description_hash, is_active. |
| [`006_create_job_applications_table.py`](006_create_job_applications_table.py) | Creates `job_applications`: job_title, company_name, apply_url (unique), date_year/month/day, job_description, yoe, skill_set, interview, offer, rejected, created_at, updated_at. Check constraints on date_month, date_day. |
| [`007_create_job_hunt_sessions_table.py`](007_create_job_hunt_sessions_table.py) | Creates `job_hunt_sessions` (created then removed in 008). |
| [`008_remove_job_hunt_sessions.py`](008_remove_job_hunt_sessions.py) | Drops `job_hunt_sessions` — premature feature removed. |
| [`009_fix_extracted_education_type.py`](009_fix_extracted_education_type.py) | Alters `extracted_education` from Text to VARCHAR(20). |

---

## Revision Chain

```
(base) → 001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009 (head)
```

---

## Adding New Migrations

```bash
alembic revision --autogenerate -m "describe your change"
```
