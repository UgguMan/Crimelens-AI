"""
CrimeLens AI — Helper Utilities
==================================
Common utility functions used across backend services.
"""

import time
from datetime import datetime, timezone
from bson import ObjectId


def to_object_id(id_str: str) -> ObjectId:
    """
    Safely convert a string to MongoDB ObjectId.
    Raises ValueError if the string is not a valid ObjectId.
    """
    if not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid ID format: {id_str}")
    return ObjectId(id_str)


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable file size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def serialize_doc(doc: dict) -> dict:
    """
    Convert a MongoDB document to JSON-serializable format.
    Converts ObjectId to string and ensures datetime serialization.
    """
    if doc is None:
        return {}
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_doc(item) if isinstance(item, dict)
                else str(item) if isinstance(item, ObjectId)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


class Timer:
    """Simple context manager for measuring execution time in milliseconds."""

    def __init__(self):
        self.start_time: float = 0
        self.elapsed_ms: int = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = int((time.perf_counter() - self.start_time) * 1000)
