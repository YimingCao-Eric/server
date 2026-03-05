from __future__ import annotations

import logging
from email.utils import parseaddr

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.job_application import JobApplication
from app.schemas.application_schema import JobApplicationUpdate
from app.schemas.email_schema import (
    EmailEvent,
    EmailEventType,
    EmailScanResponse,
)
from app.services import application_service

logger = logging.getLogger(__name__)

# Keywords for classification (case-insensitive)
_INTERVIEW_KEYWORDS = [
    "interview", "invite", "invitation", "schedule", "next steps",
    "moving forward", "assessment", "technical screen",
]
_REJECTION_KEYWORDS = [
    "unfortunately", "not moving forward", "not selected",
    "other candidates", "position has been filled",
    "we will not", "regret to inform", "thank you for applying",
    "application was not",
]
_OFFER_KEYWORDS = [
    "offer", "offer letter", "congratulations", "pleased to offer",
    "job offer",
]
_COMPANY_SUFFIXES = [
    "recruiting", "talent", "hr", "noreply", "careers", "jobs",
    "no-reply", "notifications",
]


def _get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=settings.gmail_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.gmail_client_id,
        client_secret=settings.gmail_client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
    return build("gmail", "v1", credentials=creds)


def _classify_email(subject: str, sender: str) -> EmailEventType | None:
    """Classify email by subject/sender. Priority: offer > interview_invite > rejection."""
    subject_lower = subject.lower()
    sender_lower = sender.lower()
    combined = f"{subject_lower} {sender_lower}"

    if any(kw in combined for kw in _OFFER_KEYWORDS):
        return EmailEventType.offer
    if any(kw in combined for kw in _INTERVIEW_KEYWORDS):
        return EmailEventType.interview_invite
    if any(kw in combined for kw in _REJECTION_KEYWORDS):
        return EmailEventType.rejection
    return None


def _extract_company_from_email(sender: str, subject: str) -> str | None:
    """Extract company name from sender display name or domain."""
    display_name, email_addr = parseaddr(sender.strip())

    if display_name:
        company = display_name.strip()
        company_lower = company.lower()
        for suffix in _COMPANY_SUFFIXES:
            if company_lower.endswith(f" {suffix}"):
                company = company[: -len(suffix) - 1].strip()
            elif company_lower.startswith(f"{suffix} "):
                company = company[len(suffix) + 1 :].strip()
        if company and company_lower not in ("noreply", "notifications", ""):
            return company.strip() or None

    if email_addr and "@" in email_addr:
        domain = email_addr.split("@")[-1].lower()
        if domain and domain not in ("gmail.com", "yahoo.com", "outlook.com"):
            return domain.split(".")[0].title()

    return None


async def _match_application(
    session: AsyncSession,
    company_name: str,
) -> JobApplication | None:
    """Find most recent open application matching company (no interview/offer/rejected)."""
    pattern = f"%{company_name}%"
    stmt = (
        select(JobApplication)
        .where(
            JobApplication.company_name.ilike(pattern),
            JobApplication.interview.is_(False),
            JobApplication.rejected.is_(False),
            JobApplication.offer.is_(False),
        )
        .order_by(
            JobApplication.date_year.desc(),
            JobApplication.date_month.desc(),
            JobApplication.date_day.desc(),
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def scan_inbox(session: AsyncSession) -> EmailScanResponse:
    """Scan Gmail inbox for job-related emails, classify, match to applications, update flags."""
    try:
        service = _get_gmail_service()
    except Exception as e:
        logger.error("Failed to get Gmail service: %s", e)
        raise RuntimeError(f"Gmail scan failed: {e}") from e

    try:
        list_result = service.users().messages().list(
            userId="me",
            q="is:unread newer_than:1d",
            maxResults=50,
        ).execute()
    except Exception as e:
        logger.error("Gmail messages.list failed: %s", e)
        raise RuntimeError(f"Gmail scan failed: {e}") from e

    messages = list_result.get("messages", [])
    events: list[EmailEvent] = []
    interview_count = 0
    rejection_count = 0
    offer_count = 0
    unmatched_count = 0

    for msg_ref in messages:
        msg_id = msg_ref.get("id")
        if not msg_id:
            continue
        try:
            msg = service.users().messages().get(
                userId="me",
                messageId=msg_id,
                format="metadata",
                metadataHeaders=["Subject", "From"],
            ).execute()
        except Exception as e:
            logger.warning("Failed to fetch message %s: %s", msg_id, e)
            continue

        headers = msg.get("payload", {}).get("headers", [])
        subject = ""
        sender = ""
        for h in headers:
            name = (h.get("name") or "").lower()
            value = h.get("value") or ""
            if name == "subject":
                subject = value
            elif name == "from":
                sender = value

        event_type = _classify_email(subject, sender)
        if event_type is None:
            continue

        company_name = _extract_company_from_email(sender, subject)
        app = None
        updated_flag: str | None = None

        if company_name:
            app = await _match_application(session, company_name)

        if app:
            if event_type == EmailEventType.interview_invite:
                await application_service.update_application(
                    session, app.id, JobApplicationUpdate(interview=True)
                )
                updated_flag = "interview"
                interview_count += 1
            elif event_type == EmailEventType.rejection:
                await application_service.update_application(
                    session, app.id, JobApplicationUpdate(rejected=True)
                )
                updated_flag = "rejected"
                rejection_count += 1
            elif event_type == EmailEventType.offer:
                await application_service.update_application(
                    session, app.id, JobApplicationUpdate(offer=True)
                )
                updated_flag = "offer"
                offer_count += 1
        else:
            unmatched_count += 1

        events.append(
            EmailEvent(
                event_type=event_type,
                sender=sender,
                subject=subject,
                application_id=app.id if app else None,
                company_name=company_name,
                updated_flag=updated_flag,
            )
        )

    return EmailScanResponse(
        events=events,
        total_scanned=len(events),
        interview_count=interview_count,
        rejection_count=rejection_count,
        offer_count=offer_count,
        unmatched_count=unmatched_count,
    )
