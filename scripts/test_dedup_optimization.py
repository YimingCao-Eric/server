#!/usr/bin/env python3
"""Smoke test for URL dedup optimization (Fix 1-4). Requires server at http://localhost:8000."""

from __future__ import annotations

import sys

import httpx

BASE = "http://localhost:8000"

# Seed data
APP_A = {
    "apply_url": "https://dedup-test-alpha.com/jobs/001",
    "job_title": "Backend Engineer",
    "company_name": "Dedup Alpha",
    "date_year": 2026,
    "date_month": 3,
    "date_day": 3,
    "job_description": "Python role",
    "yoe": 2,
    "skill_set": ["Python"],
}
APP_B = {
    "apply_url": "https://dedup-test-beta.com/jobs/001",
    "job_title": "ML Engineer",
    "company_name": "Dedup Beta",
    "date_year": 2026,
    "date_month": 3,
    "date_day": 2,
    "job_description": "PyTorch role",
    "yoe": 1,
    "skill_set": ["PyTorch"],
}
APP_C = {
    "apply_url": "https://dedup-test-gamma.com/jobs/001",
    "job_title": "DevOps Engineer",
    "company_name": "Dedup Gamma",
    "date_year": 2026,
    "date_month": 3,
    "date_day": 1,
    "job_description": "Docker role",
    "yoe": 2,
    "skill_set": ["Docker"],
}


def get_id_by_url(client: httpx.Client, apply_url: str) -> str | None:
    """Retrieve application ID by apply_url from list. Returns None if not found."""
    r = client.get(f"{BASE}/jobs/applications")
    if r.status_code != 200:
        return None
    for item in r.json():
        if item.get("apply_url") == apply_url:
            return str(item["id"])
    return None


def main() -> None:
    client = httpx.Client(timeout=30.0)
    seeded_ids: list[str] = []

    # Step 1 — Seed: create 3 test applications
    print("Step 1 — Seed: create 3 test applications...", end=" ")
    try:
        for name, data in [("A", APP_A), ("B", APP_B), ("C", APP_C)]:
            r = client.post(f"{BASE}/jobs/applications", json=data)
            if r.status_code == 409:
                # Leftover: retrieve existing ID
                uid = get_id_by_url(client, data["apply_url"])
                if uid:
                    seeded_ids.append(uid)
                else:
                    print(f"FAIL: 409 but could not find existing record for {name}")
                    sys.exit(1)
            else:
                r.raise_for_status()
                assert r.status_code == 201
                seeded_ids.append(str(r.json()["id"]))
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 2 — Fix 1: GET /jobs/applications/urls
    print("Step 2 — Fix 1: GET /jobs/applications/urls...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/applications/urls")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        response = r.json()
        assert isinstance(response, list), f"Expected list, got {type(response)}"
        for item in response:
            assert isinstance(item, str), f"Expected string, got {type(item)}"
            assert "job_description" not in str(item)
        urls_needed = [
            APP_A["apply_url"],
            APP_B["apply_url"],
            APP_C["apply_url"],
        ]
        for u in urls_needed:
            assert u in response, f"Missing URL {u}"
        print(f"PASS (URL list length: {len(response)})")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 3 — Fix 2: POST /jobs/applications/dedup — mixed input
    print("Step 3 — Fix 2: POST /jobs/applications/dedup (mixed)...", end=" ")
    try:
        r = client.post(
            f"{BASE}/jobs/applications/dedup",
            json={
                "urls": [
                    "https://dedup-test-alpha.com/jobs/001",
                    "https://dedup-test-beta.com/jobs/001",
                    "https://new-company.com/jobs/fresh-001",
                    "https://new-company.com/jobs/fresh-002",
                    "https://new-company.com/jobs/fresh-003",
                ]
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["new_count"] == 3
        assert data["applied_count"] == 2
        assert data["total_input"] == 5
        assert "https://new-company.com/jobs/fresh-001" in data["new_urls"]
        assert "https://dedup-test-alpha.com/jobs/001" in data["already_applied"]
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 4 — Fix 2: POST /jobs/applications/dedup — all new
    print("Step 4 — Fix 2: POST /jobs/applications/dedup (all new)...", end=" ")
    try:
        r = client.post(
            f"{BASE}/jobs/applications/dedup",
            json={
                "urls": [
                    "https://brand-new-1.com/job",
                    "https://brand-new-2.com/job",
                ]
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["new_count"] == 2
        assert data["applied_count"] == 0
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 5 — Fix 2: POST /jobs/applications/dedup — all applied
    print("Step 5 — Fix 2: POST /jobs/applications/dedup (all applied)...", end=" ")
    try:
        r = client.post(
            f"{BASE}/jobs/applications/dedup",
            json={
                "urls": [
                    "https://dedup-test-alpha.com/jobs/001",
                    "https://dedup-test-beta.com/jobs/001",
                    "https://dedup-test-gamma.com/jobs/001",
                ]
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["new_count"] == 0
        assert data["applied_count"] == 3
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 6 — Fix 2: POST /jobs/applications/dedup — empty input
    print("Step 6 — Fix 2: POST /jobs/applications/dedup (empty)...", end=" ")
    try:
        r = client.post(
            f"{BASE}/jobs/applications/dedup",
            json={"urls": []},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["new_count"] == 0
        assert data["applied_count"] == 0
        assert data["total_input"] == 0
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 7 — Fix 3: GET /jobs/applications pagination
    print("Step 7 — Fix 3: GET /jobs/applications pagination...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/applications?limit=2&offset=0")
        assert r.status_code == 200
        assert len(r.json()) == 2

        r = client.get(f"{BASE}/jobs/applications?limit=2&offset=2")
        assert r.status_code == 200
        assert len(r.json()) >= 1

        r = client.get(f"{BASE}/jobs/applications?limit=100&offset=9999")
        assert r.status_code == 200
        assert len(r.json()) == 0

        r = client.get(f"{BASE}/jobs/applications?limit=0")
        assert r.status_code == 422

        r = client.get(f"{BASE}/jobs/applications?limit=501")
        assert r.status_code == 422

        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 8 — Fix 4: GET /jobs/applications/count
    print("Step 8 — Fix 4: GET /jobs/applications/count...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/applications/count")
        assert r.status_code == 200
        data = r.json()
        assert "count" in data
        assert data["count"] >= 3
        print(f"PASS (Total applications in DB: {data['count']})")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 9 — Route order: /urls and /count not captured as /{application_id}
    print("Step 9 — Route order: /urls and /count not captured...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/applications/urls")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

        r = client.get(f"{BASE}/jobs/applications/count")
        assert r.status_code == 200
        assert "count" in r.json()
        assert isinstance(r.json()["count"], int)
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 10 — Cleanup
    print("Step 10 — Cleanup...", end=" ")
    try:
        for uid in seeded_ids:
            r = client.delete(f"{BASE}/jobs/applications/{uid}")
            if r.status_code == 405:
                print("SKIP: Cleanup skipped: no DELETE endpoint (by design)")
                break
            r.raise_for_status()
        else:
            print("PASS")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 405:
            print("SKIP: Cleanup skipped: no DELETE endpoint (by design)")
        else:
            print(f"FAIL: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    print("\nAll steps PASSED.")


if __name__ == "__main__":
    main()
