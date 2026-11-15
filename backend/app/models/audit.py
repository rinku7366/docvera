from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel

from app.core.database import Base


class AuditLog(Base):
    """
    Immutable record of every significant user action.
    user_id is nullable so unauthenticated events (e.g. failed logins) can still be logged.
    Why: audit logs must be append-only; never update or delete rows in this table.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False)          # e.g. "document.upload"
    resource_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # e.g. "document"
    resource_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)    # e.g. "42"
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
