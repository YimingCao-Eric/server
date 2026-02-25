# app/

Main application package for the AI Job Hunting Assistant backend.

---

**Navigation:** [< Back to Root](../README.md) | **Sibling:** [alembic/](../alembic/README.md)

---

## Purpose

This package contains the core application code: database infrastructure and ORM model definitions. It is structured for clean separation between database plumbing (`db/`) and domain models (`models/`).

## Files

| File | Description |
|---|---|
| [`__init__.py`](__init__.py) | Package marker. Empty file that makes `app` importable as a Python package. |

## Subdirectories

| Directory | Description |
|---|---|
| [`db/`](db/README.md) | Database infrastructure — the SQLAlchemy declarative base, metadata configuration, async engine, and session factory. |
| [`models/`](models/README.md) | SQLAlchemy ORM model definitions for the User Professional Profile schema (User, Education, WorkExperience, Skill). |
