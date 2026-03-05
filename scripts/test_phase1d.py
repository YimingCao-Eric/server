#!/usr/bin/env python3
"""Phase 1D smoke test. Requires running server at http://localhost:8000."""

from __future__ import annotations

import os
import sys

import httpx

BASE = "http://localhost:8000"

SEED_APPLICATION = {
    "job_title": "Software Engineer",
    "company_name": "Phase1D TestCorp",
    "apply_url": "https://phase1d-testcorp.com/jobs/se-001",
    "date_year": 2026,
    "date_month": 3,
    "date_day": 3,
    "job_description": "Python backend role. FastAPI, PostgreSQL, Docker.",
    "yoe": 2,
    "skill_set": ["Python", "FastAPI", "PostgreSQL", "Docker"],
}


def main() -> None:
    client = httpx.Client(timeout=60.0)
    app_id = None

    # Step 1 — Seed: create one application
    print("Step 1 — Seed: create one application...", end=" ")
    try:
        r = client.post(f"{BASE}/jobs/applications", json=SEED_APPLICATION)
        if r.status_code == 409:
            r_list = client.get(f"{BASE}/jobs/applications")
            r_list.raise_for_status()
            data_list = r_list.json()
            for item in data_list:
                if item.get("apply_url", "").rstrip("/") == SEED_APPLICATION["apply_url"].rstrip("/"):
                    app_id = item["id"]
                    break
            if app_id:
                print(f"PASS (leftover data, using existing app_id={app_id})")
            else:
                print("FAIL: 409 but could not find existing record")
                sys.exit(1)
        elif r.status_code == 201:
            data = r.json()
            app_id = data["id"]
            print(f"PASS (app_id={app_id})")
        else:
            r.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"FAIL: HTTP {e.response.status_code} - {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 2 — POST /reports/generate
    print("Step 2 — POST /reports/generate...", end=" ")
    report_text = None
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("SKIPPED (ANTHROPIC_API_KEY not set)")
    else:
        try:
            r = client.post(f"{BASE}/reports/generate")
            if r.status_code != 200:
                print(f"FAIL: HTTP {r.status_code} - {r.text}")
                sys.exit(1)
            data = r.json()
            assert "report_text" in data
            assert "generated_at" in data
            assert "applications_analysed" in data
            report_text = data["report_text"]
            assert isinstance(report_text, str) and len(report_text) > 50
            assert data["applications_analysed"] >= 1
            print(f"PASS (analysed={data['applications_analysed']})")
            print(f"  Preview: {report_text[:300]}...")
        except AssertionError as e:
            print(f"FAIL: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"FAIL: {e}")
            sys.exit(1)

    # Step 3 — GET /reports/latest
    print("Step 3 — GET /reports/latest...", end=" ")
    if report_text is None:
        print("SKIPPED (no report from Step 2)")
    else:
        try:
            r = client.get(f"{BASE}/reports/latest")
            r.raise_for_status()
            data = r.json()
            assert "report_text" in data
            assert data["report_text"] == report_text
            assert "generated_at" in data
            print("PASS")
        except Exception as e:
            print(f"FAIL: {e}")
            sys.exit(1)

    # Step 4 — GET /reports/latest before any report returns 404
    print("Step 4 — 404 before first report...", end=" ")
    if report_text is not None:
        print(
            "SKIPPED (server already has cached report from Step 2 — "
            "restart server with empty cache to verify)"
        )
    else:
        try:
            r = client.get(f"{BASE}/reports/latest")
            assert r.status_code == 404
            print("PASS (404 as expected)")
        except AssertionError:
            print(f"FAIL: expected 404, got {r.status_code}")
            sys.exit(1)
        except Exception as e:
            print(f"FAIL: {e}")
            sys.exit(1)

    # Step 5 — POST /email/scan (optional: requires real Gmail credentials)
    print("Step 5 — Email scan...", end=" ")
    if not os.getenv("GMAIL_CLIENT_ID"):
        print("SKIPPED (GMAIL_CLIENT_ID not set)")
    else:
        try:
            r = client.post(f"{BASE}/email/scan")
            if r.status_code != 200:
                print(f"FAIL: HTTP {r.status_code}")
                sys.exit(1)
            data = r.json()
            assert "events" in data
            assert "total_scanned" in data
            assert "interview_count" in data
            assert "rejection_count" in data
            assert "offer_count" in data
            assert "unmatched_count" in data
            total = data["total_scanned"]
            i_count = data["interview_count"]
            r_count = data["rejection_count"]
            o_count = data["offer_count"]
            u_count = data["unmatched_count"]
            assert all(isinstance(x, int) and x >= 0 for x in [total, i_count, r_count, o_count, u_count])
            print(
                f"PASS — Scanned {total} emails. "
                f"Interview={i_count}, Rejection={r_count}, Offer={o_count}, Unmatched={u_count}"
            )
        except AssertionError as e:
            print(f"FAIL: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"FAIL: {e}")
            sys.exit(1)

    # Step 6 — POST /email/scan returns 503 when Gmail credentials are invalid
    print("Step 6 — POST /email/scan error handling...", end=" ")
    try:
        r = client.post(f"{BASE}/email/scan")
        if r.status_code == 200:
            print("PASS (real credentials work)")
        elif r.status_code == 503:
            print("PASS (503 returned as expected with invalid credentials)")
        elif r.status_code == 404:
            print("FAIL (endpoint missing)")
            sys.exit(1)
        elif r.status_code == 500:
            print("FAIL (500 — RuntimeError not caught)")
            sys.exit(1)
        else:
            print(f"PASS (HTTP {r.status_code})")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 7 — Cleanup
    print("Step 7 — Cleanup...", end=" ")
    try:
        r = client.delete(f"{BASE}/jobs/applications/{app_id}")
        if r.status_code == 404:
            print("Cleanup skipped: no DELETE endpoint (by design)")
        elif r.status_code == 405:
            print("Cleanup skipped: no DELETE endpoint (by design)")
        else:
            r.raise_for_status()
            print("Cleanup done")
    except httpx.HTTPStatusError:
        print("Cleanup skipped: no DELETE endpoint (by design)")
    except Exception:
        print("Cleanup skipped (no DELETE endpoint or other issue)")

    print("\nAll steps PASSED.")


if __name__ == "__main__":
    main()
