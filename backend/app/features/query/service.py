import json
from sqlalchemy.orm import Session

from app.features.query.retriever import retrieve_chunks
from app.features.query.llm_client import generate_answer
from app.features.audit.service import create_log
from app.models.query import QueryRecord, QueryRequest, QueryRecordRead, CitationItem


def ask_question(
    request: QueryRequest,
    current_user_id: int,
    db: Session,
) -> QueryRecordRead:
    """
    Run the full query pipeline for one question:
    1. Retrieve relevant chunks (with ownership check)
    2. Generate an extractive answer with citations
    3. Save the query record to the database
    4. Log the action to the audit trail
    """
    retrieved = retrieve_chunks(
        document_id=request.document_id,
        question=request.question,
        current_user_id=current_user_id,
        db=db,
    )

    result = generate_answer(
        question=request.question,
        retrieved_chunks=retrieved,
        language=request.language,
        plain_language=request.plain_language,
    )

    citations_json = json.dumps(result["citations"])

    record = QueryRecord(
        user_id=current_user_id,
        document_id=request.document_id,
        question=request.question,
        answer=result["answer_text"],
        citations_json=citations_json,
        language=request.language,
        plain_language=request.plain_language,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    create_log(
        user_id=current_user_id,
        action="query.ask",
        resource_type="query_record",
        resource_id=str(record.id),
        ip_address=None,
        db=db,
    )

    citations = [CitationItem(**c) for c in result["citations"]]
    return QueryRecordRead(
        id=record.id,
        document_id=record.document_id,
        question=record.question,
        answer=record.answer,
        citations=citations,
        language=record.language,
        plain_language=record.plain_language,
        created_at=record.created_at,
    )
