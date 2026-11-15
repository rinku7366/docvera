import os
import shutil
from pathlib import Path
from app.core.config import settings


def _document_dir(document_id: int) -> Path:
    """Return the directory path for a specific document's files."""
    return Path(settings.UPLOAD_DIR) / str(document_id)


def save_upload_to_disk(file_bytes: bytes, document_id: int, filename: str) -> str:
    """
    Save uploaded file bytes to the uploads directory.
    Files are stored under UPLOAD_DIR/{document_id}/{filename}.
    Returns the absolute path as a string.
    Why per-document directories: makes cleanup simple and prevents filename collisions.
    """
    doc_dir = _document_dir(document_id)
    doc_dir.mkdir(parents=True, exist_ok=True)
    file_path = doc_dir / filename
    file_path.write_bytes(file_bytes)
    return str(file_path.resolve())


def cleanup_document_files(document_id: int) -> None:
    """
    Delete all files for a document when it is deleted.
    Why: prevent orphaned files accumulating on disk when documents are removed.
    """
    doc_dir = _document_dir(document_id)
    if doc_dir.exists():
        shutil.rmtree(doc_dir)
