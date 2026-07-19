"""
CrimeLens AI — File Validation Utilities
==========================================
Validates uploaded evidence files for security:
MIME type checking, magic byte verification, size limits, and filename sanitization.
"""

import re
import uuid
from pathlib import Path
from typing import BinaryIO

from app.config import get_settings

# Allowed MIME types mapped to our internal FileType categories
ALLOWED_MIME_TYPES: dict[str, str] = {
    # Images
    "image/jpeg": "image",
    "image/png": "image",
    "image/gif": "image",
    "image/webp": "image",
    "image/bmp": "image",
    "image/tiff": "image",
    # PDF
    "application/pdf": "pdf",
    # Text
    "text/plain": "text",
    "text/csv": "csv",
    "text/html": "text",
    "text/markdown": "text",
    # Email
    "message/rfc822": "email",
    "application/vnd.ms-outlook": "email",
    # Documents
    "application/msword": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "application/vnd.ms-excel": "document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "document",
    "application/json": "text",
}

# Magic bytes for common file types (first N bytes)
MAGIC_BYTES: dict[str, list[bytes]] = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/gif": [b"GIF87a", b"GIF89a"],
    "application/pdf": [b"%PDF"],
    "image/webp": [b"RIFF"],
    "image/bmp": [b"BM"],
}

# Dangerous file extensions that must NEVER be accepted
BLOCKED_EXTENSIONS: set[str] = {
    ".exe", ".bat", ".cmd", ".com", ".msi", ".scr", ".pif",
    ".vbs", ".js", ".ws", ".wsf", ".ps1", ".psm1",
    ".sh", ".bash", ".csh", ".ksh",
    ".dll", ".sys", ".drv",
    ".py", ".pyc", ".pyo", ".rb", ".pl",
    ".jar", ".class", ".war",
    ".php", ".asp", ".aspx", ".jsp",
}


class FileValidationError(Exception):
    """Raised when a file fails validation checks."""
    pass


def validate_file_size(file_size: int) -> None:
    """
    Ensure file size is within configured limits.
    Raises FileValidationError if file exceeds maximum allowed size.
    """
    settings = get_settings()
    if file_size > settings.max_upload_size_bytes:
        max_mb = settings.max_upload_size_mb
        actual_mb = round(file_size / (1024 * 1024), 2)
        raise FileValidationError(
            f"File size {actual_mb}MB exceeds maximum allowed {max_mb}MB"
        )
    if file_size == 0:
        raise FileValidationError("File is empty (0 bytes)")


def validate_mime_type(mime_type: str) -> str:
    """
    Check MIME type against allowlist.
    Returns the internal file type category.
    Raises FileValidationError if MIME type is not allowed.
    """
    file_type = ALLOWED_MIME_TYPES.get(mime_type)
    if file_type is None:
        raise FileValidationError(
            f"File type '{mime_type}' is not allowed. "
            f"Accepted types: images, PDFs, text files, CSVs, emails, documents."
        )
    return file_type


def validate_file_extension(filename: str) -> None:
    """
    Block dangerous file extensions.
    Raises FileValidationError if extension is in the blocklist.
    """
    ext = Path(filename).suffix.lower()
    if ext in BLOCKED_EXTENSIONS:
        raise FileValidationError(
            f"File extension '{ext}' is blocked for security reasons."
        )


def verify_magic_bytes(file_data: BinaryIO, claimed_mime: str) -> bool:
    """
    Verify file content matches claimed MIME type via magic bytes.
    Returns True if verification passes or no magic bytes defined for type.
    """
    expected_magics = MAGIC_BYTES.get(claimed_mime)
    if expected_magics is None:
        # No magic bytes defined for this type — allow through
        return True

    # Read first 16 bytes for magic byte checking
    header = file_data.read(16)
    file_data.seek(0)  # Reset file position

    for magic in expected_magics:
        if header.startswith(magic):
            return True

    return False


def sanitize_filename(original_filename: str) -> tuple[str, str]:
    """
    Generate a safe stored filename while preserving the original.
    Returns (safe_stored_name, original_cleaned_name).

    - Stored name uses UUID to prevent collisions and path traversal
    - Original name is cleaned of dangerous characters for display
    """
    # Clean the original filename for display
    cleaned = re.sub(r"[^\w\s\-.]", "_", original_filename)
    cleaned = re.sub(r"\.{2,}", ".", cleaned)  # Prevent directory traversal via ..
    cleaned = cleaned.strip(". ")

    # Generate UUID-based stored filename preserving extension
    ext = Path(cleaned).suffix.lower() if cleaned else ""
    stored_name = f"{uuid.uuid4().hex}{ext}"

    return stored_name, cleaned


def validate_upload(
    filename: str,
    mime_type: str,
    file_size: int,
    file_data: BinaryIO | None = None,
) -> tuple[str, str, str]:
    """
    Run all validation checks on an uploaded file.
    Returns (stored_filename, cleaned_original_name, file_type_category).
    Raises FileValidationError on any validation failure.
    """
    validate_file_extension(filename)
    validate_file_size(file_size)
    file_type = validate_mime_type(mime_type)

    if file_data is not None and not verify_magic_bytes(file_data, mime_type):
        raise FileValidationError(
            "File content does not match the claimed file type. "
            "The file may be corrupted or disguised."
        )

    stored_name, cleaned_name = sanitize_filename(filename)
    return stored_name, cleaned_name, file_type
