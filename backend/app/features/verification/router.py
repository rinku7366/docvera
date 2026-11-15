from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user
from app.features.verification.service import verify_query_answer
from app.models.verification import VerifyRequest, VerificationReportRead, VerificationReport, ClaimResult
from app.models.user import User
from fastapi import HTTPException
import json

router = APIRouter(prefix="/verify", tags=["verification"])


@router.post("/", response_model=VerificationReportRead)
def verify(
    request: VerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run grounding verification on a query answer."""
    return verify_query_answer(request.query_record_id, current_user.id, db)


@router.get("/{report_id}", response_model=VerificationReportRead)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a previously generated verification report. Verifies ownership."""
    report = db.query(VerificationReport).filter(VerificationReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Verification report not found.")
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
    claims = json.loads(report.claims_json) if report.claims_json else []
    return VerificationReportRead(
        id=report.id,
        query_record_id=report.query_record_id,
        claims=[ClaimResult(**c) for c in claims],
        overall_score=report.overall_score,
        created_at=report.created_at,
    )
