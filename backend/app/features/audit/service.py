from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.audit import AuditLog, AuditLogRead


def create_log(
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str],
    resource_id: Optional[str],
    ip_address: Optional[str],
    db: Session,
) -> None:
    """
    Append an immutable audit log entry.
    Why: audit logs must be append-only. Never update or delete entries.
    This function is called from every feature service after a significant action.
    user_id is Optional to allow logging unauthenticated events (failed logins, etc.)
    """
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()


def get_user_logs(user_id: int, db: Session) -> List[AuditLog]:
    """Return all audit log entries for a specific user, newest first."""
    return (
        db.query(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
