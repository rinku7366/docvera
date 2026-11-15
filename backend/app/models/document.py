import enum
import json
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel

from app.core.database import Base


# ── Status Enums ──────────────────────────────────────────────────────────────

class DocumentStatus(str, enum.Enum):
    """
    Tracks the processing pipeline stage of an uploaded document.
    Why separate statuses: the frontend shows real human-readable progress
    at each stage (Parsing → Splitting into sections → Indexing → Ready).
    """
    UPLOADING = "UPLOADING"
    PARSING = "PARSING"
    CHUNKING = "CHUNKING"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"


class ChunkType(str, enum.Enum):
    """
    Distinguishes plain text chunks from table-row chunks.
    Why: table rows must be chunked differently — one chunk per row/group —
    so that structured data is retrieved at row-level granularity, not
    mixed into flowing prose chunks.
    """
    TEXT = "TEXT"
    TABLE = "TABLE"


# ── SQLAlchemy ORM Models ─────────────────────────────────────────────────────

class Document(Base):
    """
    Represents an uploaded document owned by a user.
    filename is the sanitised on-disk name; original_filename is what the user uploaded.
    """
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus), default=DocumentStatus.UPLOADING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    chunks: Mapped[List["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    """
    A piece of text extracted from a document.
    embedding_json stores the TF-IDF vector as JSON (for simple persistence;
    in production this would be a vector database column or separate store).
    """
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_type: Mapped[ChunkType] = mapped_column(SAEnum(ChunkType), default=ChunkType.TEXT, nullable=False)
    # embedding_json is left empty in this implementation; TF-IDF is computed
    # at query time from the stored text. This avoids storing large vectors in SQLite.
    embedding_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class DocumentRead(BaseModel):
    id: int
    user_id: int
    original_filename: str
    mime_type: str
    file_size: int
    status: DocumentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ChunkRead(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    text: str
    chunk_type: ChunkType

    model_config = {"from_attributes": True}
