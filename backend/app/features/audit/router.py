from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user
from app.features.audit.service import get_user_logs
from app.models.audit import AuditLogRead
from app.models.user import User

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=List[AuditLogRead])
def get_audit_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the authenticated user's audit trail.
    Users can only see their own logs — not other users' events.
    """
    logs = get_user_logs(current_user.id, db)
    return [AuditLogRead.model_validate(log) for log in logs]
