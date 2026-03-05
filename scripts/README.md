# scripts/

Smoke tests and utilities for the AI Job Hunting Assistant backend.

---

## Project Idea (from [overview.md](../overview.md))

These scripts verify the 6-step pipeline endpoints. Run against a local server (`http://localhost:8000`). Phase 1B tests matching; Phase 1C tests applications/dedup; Phase 1D tests email scan; others test specific optimizations.

---

## Navigation

| Direction | Link |
|-----------|------|
| **Prev folder** | [../ (Root)](../README.md) |
| **Next folder** | [../app/](app/README.md) |
| **Siblings** | [alembic/](../alembic/README.md) |

---

## Files

| File | Description |
|------|-------------|
| [`test_phase1b.py`](test_phase1b.py) | **Phase 1B smoke test.** Requires `ANTHROPIC_API_KEY`. **`main()`** — creates profile, ingests jobs, runs backend match pipeline, fetches recommendations and skill histogram. Validates Step 3 matching flow. |
| [`test_phase1c.py`](test_phase1c.py) | **Phase 1C smoke test.** **`main()`** — creates two applications, tests dedup (POST /jobs/applications/dedup returns new_urls vs already_applied), GET /jobs/applications, GET /count, GET /urls. Validates Step 2 URL dedup and Step 4 application tracking. |
| [`test_phase1d.py`](test_phase1d.py) | **Phase 1D smoke test.** Requires Gmail OAuth2 env vars. **`main()`** — seeds one application, calls POST /email/scan, validates classification and flag updates. Tests Step 5 email monitoring. |
| [`test_dedup_optimization.py`](test_dedup_optimization.py) | **Dedup optimization smoke test** (Fixes 1–4). **`main()`** — seeds 3 applications, tests POST /dedup, GET /urls (token reduction), GET /applications pagination, GET /count. Verifies O(1) dedup and unbounded-list protection. |
| [`test_match_results_and_report_store.py`](test_match_results_and_report_store.py) | **Match-results and report store smoke test.** **`main()`** — ingests job, POST /jobs/match-results (OpenClaw write-back), GET /recommendations, POST /reports/store, GET /reports/latest. Validates Phase 1 write-back endpoints. |

---

## Running Scripts

```bash
# Ensure server is running
uvicorn app.main:app --reload --port 8000

# Phase 1B (requires ANTHROPIC_API_KEY)
python scripts/test_phase1b.py

# Phase 1C
python scripts/test_phase1c.py

# Phase 1D (requires Gmail OAuth2)
python scripts/test_phase1d.py

# Dedup optimization
python scripts/test_dedup_optimization.py

# Match-results and report store
python scripts/test_match_results_and_report_store.py
```
