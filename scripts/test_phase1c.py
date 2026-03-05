#!/usr/bin/env python3
"""Phase 1C smoke test. Requires running server at http://localhost:8000."""

from __future__ import annotations

import sys

import httpx

BASE = "http://localhost:8000"
NULL_UUID = "00000000-0000-0000-0000-000000000000"


def main() -> None:
    client = httpx.Client(timeout=30.0)

    # Step 1 — Create two applications
    print("Step 1 — Create two applications...", end=" ")
    app_a = {
        "job_title": "Backend Engineer",
        "company_name": "Alpha Corp",
        "apply_url": "https://alphacorp.com/jobs/backend-001",
        "date_year": 2026,
        "date_month": 3,
        "date_day": 3,
        "job_description": "Python backend role. Skills: Python, FastAPI, PostgreSQL.",
        "yoe": 2,
        "skill_set": ["Python", "FastAPI", "PostgreSQL"],
    }
    app_b = {
        "job_title": "ML Engineer",
        "company_name": "Beta AI",
        "apply_url": "https://betaai.com/jobs/ml-001",
        "date_year": 2026,
        "date_month": 3,
        "date_day": 2,
        "job_description": "ML engineering role. Skills: Python, PyTorch, Docker.",
        "yoe": 0,
        "skill_set": ["Python", "PyTorch", "Docker"],
    }
    try:
        r_a = client.post(f"{BASE}/jobs/applications", json=app_a)
        if r_a.status_code == 409:
            print(
                "FAIL: leftover data detected. Run alembic downgrade -1 && alembic upgrade head "
                "to reset, or delete rows manually."
            )
            sys.exit(1)
        r_a.raise_for_status()
        data_a = r_a.json()
        assert r_a.status_code == 201
        assert "id" in data_a
        assert "already_matched" not in data_a
        assert data_a.get("interview") is False
        assert data_a.get("offer") is False
        assert data_a.get("rejected") is False
        app_a_id = data_a["id"]

        r_b = client.post(f"{BASE}/jobs/applications", json=app_b)
        r_b.raise_for_status()
        data_b = r_b.json()
        assert r_b.status_code == 201
        assert "id" in data_b
        assert "already_matched" not in data_b
        assert data_b.get("interview") is False
        assert data_b.get("offer") is False
        assert data_b.get("rejected") is False
        app_b_id = data_b["id"]

        print(f"PASS (app_a_id={app_a_id}, app_b_id={app_b_id})")
    except httpx.HTTPStatusError as e:
        print(f"FAIL: HTTP {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 2 — Duplicate apply_url returns 409
    print("Step 2 — Duplicate apply_url returns 409...", end=" ")
    try:
        r = client.post(
            f"{BASE}/jobs/applications",
            json={
                **app_a,
                "apply_url": "https://alphacorp.com/jobs/backend-001",
            },
        )
        assert r.status_code == 409
        detail = str(r.json().get("detail", "")).lower()
        assert "apply_url" in detail
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 3 — List all applications
    print("Step 3 — List all applications...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/applications")
        r.raise_for_status()
        data = r.json()
        assert isinstance(data, list)
        ids = [str(item["id"]) for item in data]
        assert str(app_a_id) in ids
        assert str(app_b_id) in ids
        a_idx = ids.index(str(app_a_id))
        b_idx = ids.index(str(app_b_id))
        assert a_idx < b_idx, (
            "Application A (2026-03-03) should appear before B (2026-03-02)"
        )
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 4 — Get single application
    print("Step 4 — Get single application...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/applications/{app_a_id}")
        r.raise_for_status()
        data = r.json()
        assert str(data["id"]) == str(app_a_id)
        assert data["company_name"] == "Alpha Corp"
        assert data["apply_url"] == "https://alphacorp.com/jobs/backend-001"
        assert not data["apply_url"].endswith("/")
        app_a_updated_at = data.get("updated_at")
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 5 — Update flags: interview
    print("Step 5 — Update flags: interview...", end=" ")
    try:
        r = client.put(
            f"{BASE}/jobs/applications/{app_a_id}",
            json={"interview": True},
        )
        r.raise_for_status()
        data = r.json()
        assert data["interview"] is True
        assert data["offer"] is False
        assert data["rejected"] is False
        assert data.get("updated_at") != app_a_updated_at
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 6 — Update flags: offer
    print("Step 6 — Update flags: offer...", end=" ")
    try:
        r = client.put(
            f"{BASE}/jobs/applications/{app_a_id}",
            json={"offer": True},
        )
        r.raise_for_status()
        data = r.json()
        assert data["interview"] is True
        assert data["offer"] is True
        assert data["rejected"] is False
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 7 — Update flags: partial (only one field)
    print("Step 7 — Update flags: partial (only one field)...", end=" ")
    try:
        r = client.put(
            f"{BASE}/jobs/applications/{app_b_id}",
            json={"rejected": True},
        )
        r.raise_for_status()
        data = r.json()
        assert data["rejected"] is True
        assert data["interview"] is False
        assert data["offer"] is False
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 8 — GET /jobs/applications returns all apply_urls
    print("Step 8 — GET /jobs/applications returns all apply_urls...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/applications")
        r.raise_for_status()
        data = r.json()
        apply_urls = [item["apply_url"] for item in data if item.get("apply_url")]
        assert "https://alphacorp.com/jobs/backend-001" in apply_urls
        assert "https://betaai.com/jobs/ml-001" in apply_urls
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 9 — 404 on unknown id
    print("Step 9 — 404 on unknown id...", end=" ")
    try:
        r_get = client.get(f"{BASE}/jobs/applications/{NULL_UUID}")
        assert r_get.status_code == 404

        r_put = client.put(
            f"{BASE}/jobs/applications/{NULL_UUID}",
            json={"interview": True},
        )
        assert r_put.status_code == 404
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 10 — Cleanup
    print("Step 10 — Cleanup...", end=" ")
    try:
        r_a = client.delete(f"{BASE}/jobs/applications/{app_a_id}")
        if r_a.status_code == 404:
            print("Cleanup skipped: no DELETE endpoint")
        else:
            r_a.raise_for_status()
            r_b = client.delete(f"{BASE}/jobs/applications/{app_b_id}")
            r_b.raise_for_status()
            print("Cleanup done")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print("Cleanup skipped: no DELETE endpoint")
        else:
            print(f"Cleanup failed: {e}")
    except Exception as e:
        print(f"Cleanup skipped: {e}")

    print("\nAll steps PASSED.")


if __name__ == "__main__":
    main()
