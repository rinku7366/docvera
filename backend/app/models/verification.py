import json
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel

from app.core.database import Base


class VerificationReport(Base):
    """
    Stores grounding verification results for a query answer.
    claims_json is a JSON array of per-claim grounding results.
    overall_score is the fraction of claims deemed grounded (0.0 – 1.0).
    """
    __tablename__ = "verification_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query_record_id: Mapped[int] = mapped_column(Integer, ForeignKey("query_records.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    claims_json: Mapped[str] = mapped_column(Text, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class ClaimResult(BaseModel):
    claim: str
    is_grounded: bool
    best_chunk: str
    score: float


class VerificationReportRead(BaseModel):
    id: int
    query_record_id: int
    claims: List[ClaimResult]
    overall_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class VerifyRequest(BaseModel):
    query_record_id: int
