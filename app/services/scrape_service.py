from __future__ import annotations

import os

import httpx
from fastapi import HTTPException, status

from app.schemas.job_scrape_schema import ScrapeRequest

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

_SCRAPER_WEBHOOKS: dict[str, str | None] = {
    "linkedin": os.getenv("SCRAPER_WEBHOOK_LINKEDIN"),
    "indeed": os.getenv("SCRAPER_WEBHOOK_INDEED"),
    "glassdoor": os.getenv("SCRAPER_WEBHOOK_GLASSDOOR"),
}


def _get_webhook_url(website: str) -> str:
    if website not in _SCRAPER_WEBHOOKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unsupported website: '{website}'. Supported: {sorted(_SCRAPER_WEBHOOKS.keys())}",
        )
    url = _SCRAPER_WEBHOOKS[website]
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scraper for '{website}' is not configured. Set SCRAPER_WEBHOOK_{website.upper()} env var.",
        )
    return url


async def trigger_scrape(data: ScrapeRequest) -> dict[str, str]:
    webhook_url = _get_webhook_url(data.website)

    payload = {
        "job_title": data.job_title,
        "location": data.location,
        "date_posted_filter": data.date_posted_filter,
        "max_results": data.max_results,
        "ingest_callback_url": f"{BACKEND_BASE_URL}/jobs/ingest",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Scraper for '{data.website}' is unavailable (connection refused)",
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Scraper for '{data.website}' timed out",
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Scraper returned error {exc.response.status_code}",
            )

    return {
        "message": "Scraping triggered",
        "website": data.website,
        "status": "sent_to_scraper",
    }
