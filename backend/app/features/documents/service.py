from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.document import Document, DocumentStatus, Chunk
from app.features.documents.parser import parse_pdf, parse_csv, parse_text
from app.features.documents.chunker import chunk_text, chunk_table_rows
from app.features.documents.storage import save_upload_to_disk
from app.utils.logger import logger


def process_document(
    db: Session,
    document: Document,
    file_bytes: bytes,
    filepath_on_disk: str,
) -> None:
    """
    Orchestrate the full document processing pipeline.
    Updates the document status at each stage so the frontend can show
    real-time progress (Parsing → Splitting into sections → Indexing → Ready).

    Stages:
      PARSING   — extract raw text / rows from the file
      CHUNKING  — split into retrievable pieces
      INDEXING  — save chunks to the database (TF-IDF index built at query time)
      READY     — document is available for querying

    If any stage fails, the document status is set to FAILED and the
    error is logged. The exception is NOT re-raised so the HTTP response
    has already been sent (upload returns 200, processing is synchronous here
    but status is checked by the frontend via polling GET /documents/{id}).
    """
    try:
        # ── PARSING ──────────────────────────────────────────────────────────
        _set_status(db, document, DocumentStatus.PARSING)

        mime = document.mime_type
        if mime == "application/pdf":
            pages = parse_pdf(filepath_on_disk)
            raw_chunks = []
            for page in pages:
                raw_chunks.extend(chunk_text(page["text"]))
        elif mime == "text/csv":
            rows = parse_csv(filepath_on_disk)
            raw_chunks = chunk_table_rows(rows)
        else:
            pages = parse_text(filepath_on_disk)
            raw_chunks = []
            for page in pages:
                raw_chunks.extend(chunk_text(page["text"]))

        # ── CHUNKING ─────────────────────────────────────────────────────────
        _set_status(db, document, DocumentStatus.CHUNKING)

        # ── INDEXING ─────────────────────────────────────────────────────────
        _set_status(db, document, DocumentStatus.INDEXING)

        db_chunks = []
        for i, c in enumerate(raw_chunks):
            db_chunks.append(
                Chunk(
                    document_id=document.id,
                    chunk_index=i,
                    text=c["text"],
                    chunk_type=c["chunk_type"],
                )
            )
        db.add_all(db_chunks)
        db.commit()

        # ── READY ─────────────────────────────────────────────────────────────
        _set_status(db, document, DocumentStatus.READY)
        logger.info(f"Document {document.id} processed: {len(db_chunks)} chunks indexed.")

    except Exception as exc:
        logger.error(f"Document {document.id} processing failed: {exc}")
        _set_status(db, document, DocumentStatus.FAILED)


def _set_status(db: Session, document: Document, status: DocumentStatus) -> None:
    """Helper: update document status and flush to DB immediately."""
    document.status = status
    db.add(document)
    db.commit()
