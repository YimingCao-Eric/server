from __future__ import annotations

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.job_scrape_schema import ScrapeRequest


def _get_webhook_url(website: str) -> str:
    mapping = {
        "linkedin": settings.scraper_webhook_linkedin,
        "indeed": settings.scraper_webhook_indeed,
        "glassdoor": settings.scraper_webhook_glassdoor,
    }
    if website.lower() not in mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unsupported website: '{website}'. Supported: {sorted(mapping.keys())}",
        )
    url = mapping.get(website.lower())
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
        "ingest_callback_url": f"{settings.backend_base_url}/jobs/ingest",
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
