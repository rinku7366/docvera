import json
from datetime import datetime, timezone
from typing import Optional, List, Any

from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel

from app.core.database import Base


class QueryRecord(Base):
    """
    Stores one question-answer exchange for a document.
    citations_json stores the list of cited chunks as a JSON string.
    language and plain_language capture the display preferences at query time.
    """
    __tablename__ = "query_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    # citations_json: JSON array of {chunk_index, excerpt, score}
    citations_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String, default="en")
    plain_language: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class CitationItem(BaseModel):
    chunk_index: int
    excerpt: str
    score: float


class QueryRequest(BaseModel):
    document_id: int
    question: str
    language: str = "en"
    plain_language: bool = False


class QueryRecordRead(BaseModel):
    id: int
    document_id: int
    question: str
    answer: str
    citations: List[CitationItem] = []
    language: str
    plain_language: bool
    created_at: datetime

    model_config = {"from_attributes": True}
