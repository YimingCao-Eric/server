from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.email_schema import EmailScanResponse
from app.services import email_service

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/scan", response_model=EmailScanResponse)
async def scan_email(
    session: AsyncSession = Depends(get_session),
) -> EmailScanResponse:
    try:
        return await email_service.scan_inbox(session)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
