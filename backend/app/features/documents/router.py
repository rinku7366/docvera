import os
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_document_ownership
from app.features.auth.dependencies import get_current_user
from app.features.documents.validator import validate_upload_file
from app.features.documents.storage import save_upload_to_disk, cleanup_document_files
from app.features.documents.service import process_document
from app.features.audit.service import create_log
from app.models.document import Document, DocumentStatus, DocumentRead
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentRead, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a document for processing.
    Steps: validate → create DB record → save to disk → process pipeline → return.
    The document status is updated at each processing stage.
    """
    # Validate before touching the file content (Rule 6)
    validate_upload_file(file)

    file_bytes = file.file.read()

    # Create the DB record first to get an ID for the storage directory
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        original_filename=file.filename,
        mime_type=file.content_type,
        file_size=len(file_bytes),
        status=DocumentStatus.UPLOADING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Save to disk using document ID as directory name
    filepath = save_upload_to_disk(file_bytes, document.id, file.filename)

    # Process synchronously (parse, chunk, index)
    process_document(db, document, file_bytes, filepath)
    db.refresh(document)

    create_log(
        user_id=current_user.id,
        action="document.upload",
        resource_type="document",
        resource_id=str(document.id),
        ip_address=None,
        db=db,
    )

    return document


@router.get("/", response_model=List[DocumentRead])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return only documents belonging to the authenticated user."""
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return docs


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single document. Verifies the document belongs to the current user."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    verify_document_ownership(document.user_id, current_user.id)
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a document and its uploaded files. Verifies ownership first."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    verify_document_ownership(document.user_id, current_user.id)

    cleanup_document_files(document_id)
    db.delete(document)
    db.commit()

    create_log(
        user_id=current_user.id,
        action="document.delete",
        resource_type="document",
        resource_id=str(document_id),
        ip_address=None,
        db=db,
    )
