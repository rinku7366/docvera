import os
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

# Magic byte signatures for file type verification.
# Why: the Content-Type header can be forged by a client. Reading the
# first bytes of the file (magic bytes) is a reliable check that the
# file is actually what it claims to be.
MAGIC_BYTES = {
    "application/pdf": b"%PDF",
}


def validate_upload_file(file: UploadFile) -> None:
    """
    Validate an uploaded file before it is saved or parsed.
    Checks performed in order:
    1. MIME type is in the allowed list.
    2. File size does not exceed the configured limit.
    3. For PDFs: magic bytes confirm it is actually a PDF.
    Raises HTTP 400 with a plain-language message on any failure.
    """
    # 1. MIME type check
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"File type '{file.content_type}' is not supported. "
                "Please upload a PDF, CSV, or plain text file."
            ),
        )

    # 2. File size check — read the file into memory to measure it,
    #    then seek back to 0 so the caller can still read it.
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)     # Seek back to start

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"This file is too large ({file_size // (1024*1024)} MB). "
                f"Please upload a file smaller than {settings.MAX_FILE_SIZE_MB} MB."
            ),
        )

    # 3. Magic byte check for PDFs
    if file.content_type == "application/pdf":
        header = file.file.read(4)
        file.file.seek(0)
        if header != MAGIC_BYTES["application/pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The file does not appear to be a valid PDF. Please check the file and try again.",
            )
