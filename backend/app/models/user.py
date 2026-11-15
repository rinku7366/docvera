from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, EmailStr
from app.core.database import Base


# ── SQLAlchemy ORM Model ──────────────────────────────────────────────────────

class User(Base):
    """
    Represents a registered DocVera user.
    email is the unique identifier used for login.
    hashed_password is a bcrypt hash — never the plain-text password.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Input schema for user registration."""
    email: str
    password: str


class UserRead(BaseModel):
    """Output schema — never includes hashed_password."""
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT token response returned after successful login."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded JWT payload extracted by the auth dependency."""
    user_id: Optional[int] = None
