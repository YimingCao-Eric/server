# app/models/

SQLAlchemy ORM models for the AI Job Hunting Assistant.

---

**Navigation:** [< Back to app/](../README.md) | [<< Back to Root](../../README.md) | **Sibling:** [db/](../db/README.md)

---

## Purpose

This package defines six database tables across two domains: **User Profile** (five related tables) and **Job Ingestion** (one standalone table). All models inherit from `app.db.base.Base`, use UUID primary keys, and follow the SQLAlchemy 2.0 `mapped_column` style with full Python type annotations.

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package-level re-exports. Imports and exposes `User`, `Education`, `WorkExperience`, `Project`, `Skill`, and `Job`. Defines `__all__` for explicit public API. |
| [`user.py`](user.py) | **`User` model** — maps to the `users` table. Mandatory fields: `name`, `email` (unique, indexed). Optional fields: `phone`, `linkedin_url`, `github_url`, `personal_website`, `location_country`, `location_province_state`, `location_city`. Timestamps: `created_at` (auto on insert), `updated_at` (auto on insert and update via `onupdate`). Defines four `relationship()` attributes (`educations`, `work_experiences`, `projects`, `skills`) with `back_populates` and `cascade="all, delete-orphan"`. |
| [`education.py`](education.py) | **`Education` model** — maps to the `educations` table. Each row represents one education entry for a user. Mandatory fields: `institution_name`, `degree`, `field_of_study`, full address (`address_country`, `address_province_state`, `address_city`), `start_date`, `graduate_date`. Optional: `gpa`, `description`. Foreign key `user_id` references `users.id` with `ON DELETE CASCADE`. Check constraint ensures `graduate_date >= start_date`. Dates stored as `DATE` type (use first-of-month for month+year, e.g. `2024-09-01`). |
| [`work_experience.py`](work_experience.py) | **`WorkExperience` model** — maps to the `work_experiences` table. Each row is one work experience entry. Mandatory fields: `company_name` (indexed), `job_title`, `start_date`, `is_remote` (Boolean, defaults to `false`), `description`. Optional: `location_country`, `location_province_state`, `location_city`, `end_date` (NULL = currently working). Foreign key `user_id → users.id CASCADE`. Check constraint: `end_date IS NULL OR end_date >= start_date`. |
| [`project.py`](project.py) | **`Project` model** — maps to the `projects` table. Each row is one project entry. Mandatory fields: `project_title`, `start_date`, `description`. Optional: `end_date` (NULL = ongoing). Foreign key `user_id → users.id CASCADE`. Check constraint: `end_date IS NULL OR end_date >= start_date`. |
| [`skill.py`](skill.py) | **`Skill` model** — maps to the `skills` table. One row per skill (normalized, no multi-value columns). Fields: `skill_name` (indexed), `skill_category` (PostgreSQL ENUM constrained to: `language`, `framework`, `database`, `tooling`, `machine_learning`, `soft_skill`). Also defines the `SkillCategory` Python enum class used for type-safe category values. Foreign key `user_id → users.id CASCADE`. |
| [`job.py`](job.py) | **`Job` model** — maps to the `jobs` table. **Standalone table** (no FK to users). Stores job postings from external sources. Mandatory fields: `website`, `job_title`, `company`, `job_description`. Optional: `location`, `post_datetime`, `source_url`, `search_keyword`, `search_location`. Indexes: `website`, `job_title`, `company`, partial unique on `source_url` (where NOT NULL), composite dedup index on `(website, job_title, company)`. |

## Relationships

```
User  ──1:N──>  Education        (user.educations / education.user)
User  ──1:N──>  WorkExperience   (user.work_experiences / work_experience.user)
User  ──1:N──>  Project          (user.projects / project.user)
User  ──1:N──>  Skill            (user.skills / skill.user)

Job   (standalone — no relationships yet)
```

All user relationships use `back_populates` for bidirectional access and `cascade="all, delete-orphan"` on the parent side so that deleting a `User` automatically removes all associated child records.
