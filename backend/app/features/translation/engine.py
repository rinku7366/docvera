from fastapi import HTTPException, status
from app.core.config import settings

try:
    from deep_translator import GoogleTranslator
    _DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    _DEEP_TRANSLATOR_AVAILABLE = False


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """
    Translate text using the deep-translator library (Google Translate API).

    IMPORTANT — what this actually does:
    This calls Google Translate via the deep-translator library.
    It is NOT a custom translation model. Translation quality depends on
    Google Translate. The UI must label translated content clearly:
    "Translated by Google Translate".

    Raises HTTP 400 if the target language is not supported.
    Raises HTTP 503 if the translation service is unavailable.
    """
    if target_lang not in settings.SUPPORTED_TARGET_LANGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{target_lang}' is not supported. Supported: {settings.SUPPORTED_TARGET_LANGS}",
        )

    if not _DEEP_TRANSLATOR_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation service is not available. Please install deep-translator.",
        )

    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        # Google Translate has a character limit (~5000 chars per request).
        # For longer texts, split and translate in chunks.
        MAX_CHARS = 4500
        if len(text) <= MAX_CHARS:
            return translator.translate(text)
        else:
            parts = [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
            return " ".join(translator.translate(part) for part in parts)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation failed. Please try again later.",
        )
