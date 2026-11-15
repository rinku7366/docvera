from sqlalchemy.orm import Session
from app.features.translation.engine import translate_text
from app.features.audit.service import create_log
from app.models.translation import TranslationRecord, TranslationRequest, TranslationRecordRead


def translate_and_save(
    request: TranslationRequest,
    user_id: int,
    db: Session,
) -> TranslationRecordRead:
    """Translate text and persist the result for the user."""
    translated = translate_text(
        text=request.text,
        target_lang=request.target_lang,
        source_lang=request.source_lang,
    )

    record = TranslationRecord(
        user_id=user_id,
        source_text=request.text,
        translated_text=translated,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    create_log(
        user_id=user_id,
        action="translation.create",
        resource_type="translation_record",
        resource_id=str(record.id),
        ip_address=None,
        db=db,
    )

    return TranslationRecordRead.model_validate(record)
