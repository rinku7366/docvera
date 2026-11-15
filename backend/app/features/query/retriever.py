from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_document_ownership
from app.models.document import Document, Chunk
from app.features.query.vector_store import vector_store


def retrieve_chunks(
    document_id: int,
    question: str,
    current_user_id: int,
    db: Session,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """
    Retrieve the most relevant chunks for a question from a document.
    Ownership is verified before any data is returned.
    If the document's index is not yet in memory, it is built from the DB.
    Returns list of (chunk_text, score).
    """
    # Ownership check — raises 403 if the document belongs to another user
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    verify_document_ownership(document.user_id, current_user_id)

    # Build index from DB if not cached (e.g. after server restart)
    if document_id not in vector_store._store:
        chunks = db.query(Chunk).filter(Chunk.document_id == document_id).order_by(Chunk.chunk_index).all()
        chunk_texts = [c.text for c in chunks]
        vector_store.build_for_document(document_id, chunk_texts)

    return vector_store.query(document_id, question, top_k)
