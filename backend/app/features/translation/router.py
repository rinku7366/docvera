from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.features.auth.dependencies import get_current_user
from app.features.translation.service import translate_and_save
from app.models.translation import TranslationRequest, TranslationRecordRead, TranslationRecord
from app.models.user import User

router = APIRouter(prefix="/translation", tags=["translation"])


@router.post("/text", response_model=TranslationRecordRead)
def translate_text_endpoint(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Translate a block of text and save the result."""
    return translate_and_save(request, current_user.id, db)


@router.get("/history", response_model=List[TranslationRecordRead])
def translation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's translation history."""
    records = (
        db.query(TranslationRecord)
        .filter(TranslationRecord.user_id == current_user.id)
        .order_by(TranslationRecord.created_at.desc())
        .all()
    )
    return [TranslationRecordRead.model_validate(r) for r in records]
