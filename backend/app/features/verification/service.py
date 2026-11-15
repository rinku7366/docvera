import json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_document_ownership
from app.features.verification.claim_extractor import extract_claims
from app.features.verification.grounding_checker import check_claim_grounding
from app.features.audit.service import create_log
from app.models.query import QueryRecord
from app.models.verification import VerificationReport, VerificationReportRead, ClaimResult


def verify_query_answer(
    query_record_id: int,
    current_user_id: int,
    db: Session,
) -> VerificationReportRead:
    """
    Generate a grounding verification report for a query answer.
    Steps:
    1. Load the query record (with ownership check)
    2. Extract the citations (source chunks used to generate the answer)
    3. Split the answer into individual claims
    4. Check each claim against the source chunks
    5. Compute overall grounding score (fraction of claims grounded)
    6. Persist and return the report
    """
    record = db.query(QueryRecord).filter(QueryRecord.id == query_record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Query record not found.")

    # Ownership check: query record belongs to the user
    if record.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")

    # Source chunks are the cited excerpts stored with the query record
    raw_citations = json.loads(record.citations_json) if record.citations_json else []
    source_chunks = [c.get("excerpt", "") for c in raw_citations if c.get("excerpt")]

    claims = extract_claims(record.answer)
    claim_results = [check_claim_grounding(claim, source_chunks) for claim in claims]

    grounded_count = sum(1 for r in claim_results if r["is_grounded"])
    overall_score = grounded_count / len(claim_results) if claim_results else 0.0

    report = VerificationReport(
        query_record_id=query_record_id,
        user_id=current_user_id,
        claims_json=json.dumps(claim_results),
        overall_score=overall_score,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    create_log(
        user_id=current_user_id,
        action="verification.run",
        resource_type="verification_report",
        resource_id=str(report.id),
        ip_address=None,
        db=db,
    )

    return VerificationReportRead(
        id=report.id,
        query_record_id=report.query_record_id,
        claims=[ClaimResult(**r) for r in claim_results],
        overall_score=report.overall_score,
        created_at=report.created_at,
    )
