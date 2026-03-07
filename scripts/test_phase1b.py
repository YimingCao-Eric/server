#!/usr/bin/env python3
"""Phase 1B smoke test. Requires running server at http://localhost:8000 and ANTHROPIC_API_KEY."""

from __future__ import annotations

import sys

import httpx

BASE = "http://localhost:8000"


def main() -> None:
    client = httpx.Client(timeout=60.0)

    # Step 1 — Create test profile
    print("Step 1: Create profile...", end=" ")
    try:
        r = client.post(
            f"{BASE}/profiles",
            json={
                "name": "Test User",
                "email": "test_phase1b@example.com",
                "phone": "+1-000-000-0000",
                "location_country": "Canada",
                "location_province_state": "BC",
                "location_city": "Vancouver",
                "educations": [
                    {
                        "institution_name": "University of British Columbia",
                        "degree": "Master of Engineering",
                        "field_of_study": "Electrical and Computer Engineering",
                        "address_country": "Canada",
                        "address_province_state": "BC",
                        "address_city": "Vancouver",
                        "start_date": "2022-09",
                        "graduate_date": "2024-05",
                    }
                ],
                "work_experiences": [
                    {
                        "company_name": "Test Corp",
                        "job_title": "Software Engineer",
                        "location_country": "Canada",
                        "location_province_state": "BC",
                        "location_city": "Vancouver",
                        "start_date": "2024-06",
                        "end_date": None,
                        "is_remote": True,
                        "description": "Backend development with Python and FastAPI",
                    }
                ],
                "projects": [],
                "skills": [
                    {"skill_name": "Python", "skill_category": "language"},
                    {"skill_name": "FastAPI", "skill_category": "framework"},
                    {"skill_name": "PostgreSQL", "skill_category": "database"},
                    {"skill_name": "Docker", "skill_category": "tooling"},
                    {"skill_name": "SQLAlchemy", "skill_category": "framework"},
                ],
            },
        )
        r.raise_for_status()
        profile_id = r.json()["id"]
        print(f"PASS (profile_id={profile_id})")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 2 — Ingest 3 test jobs
    print("Step 2: Ingest jobs...", end=" ")
    job_ids = []
    jobs_data = [
        {
            "website": "linkedin",
            "job_title": "Backend Software Engineer",
            "company": "TechCorp",
            "location": "Vancouver, BC",
            "job_description": "We are looking for a Backend Software Engineer with 2+ years of experience. Required skills: Python, FastAPI, PostgreSQL, Docker, REST APIs. Bachelor's degree in Computer Science or related field required. You will build scalable APIs and data pipelines.",
            "post_datetime": "2026-03-03T10:00:00Z",
            "job_url": "https://linkedin.com/jobs/test-backend-001",
            "search_keyword": "software engineer",
            "search_location": "Canada",
        },
        {
            "website": "indeed",
            "job_title": "Research Scientist",
            "company": "AI Lab",
            "location": "Toronto, ON",
            "job_description": "PhD required in Machine Learning or Computer Science. 8+ years of experience in deep learning research. Publications in top conferences required. Skills: PyTorch, CUDA, C++, MATLAB.",
            "post_datetime": "2026-03-03T10:00:00Z",
            "job_url": "https://indeed.com/jobs/test-research-001",
            "search_keyword": "software engineer",
            "search_location": "Canada",
        },
        {
            "website": "glassdoor",
            "job_title": "Senior Software Engineer",
            "company": "BigCo",
            "location": "Vancouver, BC",
            "job_description": "10+ years of experience required. Bachelor's or Master's degree. Skills: Python, Go, Kubernetes, AWS, Terraform, system design at massive scale.",
            "post_datetime": "2026-03-03T10:00:00Z",
            "job_url": "https://glassdoor.com/jobs/test-senior-001",
            "search_keyword": "software engineer",
            "search_location": "Canada",
        },
    ]
    try:
        for j in jobs_data:
            r = client.post(f"{BASE}/jobs/ingest", json=j)
            r.raise_for_status()
            data = r.json()
            assert data.get("already_exists") is False
            job_ids.append(data["id"])
        print(f"PASS (job_ids={job_ids})")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 3 — GET resume-text
    print("Step 3: GET resume-text...", end=" ")
    try:
        r = client.get(f"{BASE}/profiles/{profile_id}/resume-text")
        r.raise_for_status()
        data = r.json()
        assert "resume_text" in data
        assert data.get("token_estimate", 0) > 0
        print("PASS")
        print("  resume_text (first 200 chars):", data["resume_text"][:200] + "...")
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 4 — POST /jobs/match
    print("Step 4: POST /jobs/match...", end=" ")
    try:
        r = client.post(
            f"{BASE}/jobs/match",
            json={
                "job_ids": [str(jid) for jid in job_ids],
                "profile_id": str(profile_id),
            },
        )
        r.raise_for_status()
        data = r.json()
        assert data["total"] == 3

        results = {r["job_id"]: r for r in data["results"]}
        job_b_id = job_ids[1]
        job_c_id = job_ids[2]
        job_a_id = job_ids[0]

        rb = results.get(str(job_b_id))
        rc = results.get(str(job_c_id))
        ra = results.get(str(job_a_id))

        assert rb, "Job B not in results"
        assert rb.get("skipped_reason") == "education_gate", (
            f"Job B expected education_gate, got {rb.get('skipped_reason')}"
        )
        assert rc, "Job C not in results"
        assert rc.get("skipped_reason") == "yoe_gate", (
            f"Job C expected yoe_gate, got {rc.get('skipped_reason')}"
        )
        assert ra, "Job A not in results"
        assert ra.get("match_level") in ("fully_matched", "half_matched"), (
            f"Job A expected fully_matched or half_matched, got {ra.get('match_level')}"
        )

        print("PASS")
        print("  results:", data["results"])
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 5 — GET recommendations
    print("Step 5: GET recommendations...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/recommendations/{profile_id}")
        r.raise_for_status()
        recs = r.json()
        rec_ids = [r["id"] for r in recs]
        assert str(job_a_id) in rec_ids, f"Job A should appear, got {rec_ids}"
        assert str(job_b_id) not in rec_ids, "Job B should NOT appear"
        assert str(job_c_id) not in rec_ids, "Job C should NOT appear"
        print("PASS")
        print("  recommendations:", recs)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 6 — GET skill-histogram
    print("Step 6: GET skill-histogram...", end=" ")
    try:
        r = client.get(f"{BASE}/jobs/skill-histogram")
        r.raise_for_status()
        hist = r.json()
        assert isinstance(hist, list) and len(hist) > 0
        skills_lower = [h["skill"].lower() for h in hist]
        assert any("python" in s for s in skills_lower), (
            f"Python should appear in top results, got {hist[:10]}"
        )
        print("PASS")
        print("  top 10 skills:", hist[:10])
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    # Step 7 — Cleanup
    print("Step 7: Cleanup...", end=" ")
    try:
        r = client.delete(f"{BASE}/profiles/{profile_id}")
        r.raise_for_status()
        print("Cleanup done")
    except Exception as e:
        print(f"Cleanup skipped: {e}")

    print("\nAll steps PASSED.")


if __name__ == "__main__":
    main()
