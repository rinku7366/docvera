import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user
from app.features.query.service import ask_question
from app.models.query import QueryRequest, QueryRecordRead, QueryRecord, CitationItem
from app.models.user import User

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryRecordRead)
def ask(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ask a question about a document. Returns an extractive answer with citations."""
    return ask_question(request, current_user.id, db)


@router.get("/history", response_model=List[QueryRecordRead])
def history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's query history."""
    records = (
        db.query(QueryRecord)
        .filter(QueryRecord.user_id == current_user.id)
        .order_by(QueryRecord.created_at.desc())
        .all()
    )
    result = []
    for r in records:
        citations = json.loads(r.citations_json) if r.citations_json else []
        result.append(QueryRecordRead(
            id=r.id,
            document_id=r.document_id,
            question=r.question,
            answer=r.answer,
            citations=[CitationItem(**c) for c in citations],
            language=r.language,
            plain_language=r.plain_language,
            created_at=r.created_at,
        ))
    return result
