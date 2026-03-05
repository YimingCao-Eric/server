from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReportStoreRequest(BaseModel):
    report_text: str
    applications_analysed: int = 0
    # Default 0 preserves backward compatibility.
    # OpenClaw should pass the actual count when calling POST /reports/store.


class ReportResponse(BaseModel):
    report_text: str
    applications_analysed: int = 0
    generated_at: datetime
