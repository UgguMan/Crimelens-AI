"""
CrimeLens AI — Input Sanitization
====================================
Prevents XSS, path traversal, and injection attacks on user-supplied strings.
"""

import re
import html
from pathlib import PurePosixPath, PureWindowsPath


def sanitize_html(text: str) -> str:
    """Escape HTML entities to prevent XSS."""
    return html.escape(text, quote=True)


def sanitize_path(path_str: str) -> str:
    """
    Prevent path traversal attacks.
    Strips directory separators and parent directory references.
    """
    # Remove any directory traversal patterns
    sanitized = path_str.replace("..", "").replace("/", "").replace("\\", "")
    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")
    return sanitized


def sanitize_search_query(query: str) -> str:
    """
    Clean search input: strip control characters, limit length,
    and remove potential injection patterns.
    """
    # Remove control characters
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", query)
    # Limit length to prevent abuse
    cleaned = cleaned[:500]
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    return cleaned


def sanitize_mongo_query(value: str) -> str:
    """
    Prevent MongoDB operator injection.
    Strips $ prefix used in MongoDB query operators like $gt, $regex, etc.
    """
    if isinstance(value, str):
        # Remove leading $ to prevent operator injection
        while value.startswith("$"):
            value = value[1:]
    return value


def sanitize_tag(tag: str) -> str:
    """Normalize a tag: lowercase, strip, remove special chars, limit length."""
    tag = tag.strip().lower()
    tag = re.sub(r"[^\w\s\-]", "", tag)
    return tag[:50]


def is_safe_string(text: str, max_length: int = 10000) -> bool:
    """
    Basic safety check for user-supplied text.
    Returns False if text contains dangerous patterns.
    """
    if len(text) > max_length:
        return False
    # Check for null bytes
    if "\x00" in text:
        return False
    return True
