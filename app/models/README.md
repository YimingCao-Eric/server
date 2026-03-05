# app/models/

SQLAlchemy ORM models for the AI Job Hunting Assistant.

---

## Project Idea (from [overview.md](../../overview.md))

Models map to PostgreSQL tables: **User Profile** (users, educations, work_experiences, projects, skills) and **Jobs** (jobs for market intelligence, job_applications for Eric's confirmed applications). Two-table separation: `jobs` = all scraped jobs; `job_applications` = application history.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../db/](db/README.md) |
| **Next folder** | [../schemas/](schemas/README.md) |
| **Siblings** | [core/](../core/README.md) · [services/](../services/README.md) · [routers/](../routers/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`__init__.py`](__init__.py) | Re-exports `User`, `Education`, `WorkExperience`, `Project`, `Skill`, `Job`, `JobApplication`. Defines `__all__` for explicit public API. |
| [`user.py`](user.py) | **`User`** — maps to `users`. Fields: `name`, `email` (unique), `phone`, `linkedin_url`, `github_url`, `personal_website`, `location_country`/`province_state`/`city`, `created_at`, `updated_at`. Relationships: `educations`, `work_experiences`, `projects`, `skills` (cascade delete). |
| [`education.py`](education.py) | **`Education`** — maps to `educations`. FK `user_id` → users. Fields: `institution_name`, `degree`, `field_of_study`, address, `start_date`, `graduate_date`, `gpa`, `description`. Check: `graduate_date >= start_date`. |
| [`work_experience.py`](work_experience.py) | **`WorkExperience`** — maps to `work_experiences`. FK `user_id`. Fields: `company_name`, `job_title`, `location_*`, `start_date`, `end_date`, `is_remote`, `description`. Check: `end_date >= start_date` or NULL. |
| [`project.py`](project.py) | **`Project`** — maps to `projects`. FK `user_id`. Fields: `project_title`, `start_date`, `end_date`, `description`. Check: `end_date >= start_date` or NULL. |
| [`skill.py`](skill.py) | **`Skill`** — maps to `skills`. FK `user_id`. Fields: `skill_name`, `skill_category` (ENUM: language, framework, database, tooling, machine_learning, soft_skill). |
| [`job.py`](job.py) | **`Job`** — maps to `jobs` (standalone). Fields: `website`, `job_title`, `company`, `location`, `job_description`, `post_datetime`, `source_url` (unique when not null), `search_keyword`, `search_location`, `created_at`, `updated_at`. Matching: `match_level`, `match_reason`, `matched_at`, `is_active`, `extracted_yoe`, `extracted_skills`, `extracted_education` (VARCHAR 20), `raw_description_hash`. Indexes: website, job_title, company, source_url, dedup composite. |
| [`job_application.py`](job_application.py) | **`JobApplication`** — maps to `job_applications`. Stores confirmed applications. Fields: `job_title`, `company_name`, `apply_url` (unique — must equal job `source_url` for dedup), `date_year`/`month`/`day`, `job_description`, `yoe`, `skill_set`, `interview`, `offer`, `rejected`, `created_at`, `updated_at`. |

---

## Relationships

```
User  ──1:N──>  Education
User  ──1:N──>  WorkExperience
User  ──1:N──>  Project
User  ──1:N──>  Skill

Job              (standalone)
JobApplication   (standalone — apply_url references jobs.source_url by convention)
```
