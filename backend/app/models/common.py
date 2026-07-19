"""
CrimeLens AI — Common Model Utilities
=======================================
Shared Pydantic types, mixins, and response wrappers used across all models.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from bson import ObjectId
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class PyObjectId(str):
    """
    Custom type that accepts MongoDB ObjectId and serializes to string.
    Compatible with Pydantic v2 schema generation.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def _validate(cls, value: Any) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, str) and ObjectId.is_valid(value):
            return value
        raise ValueError(f"Invalid ObjectId: {value}")


def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


class TimestampMixin(BaseModel):
    """Mixin providing created_at and updated_at fields."""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: list[Any] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class APIResponse(BaseModel):
    """Standard API response envelope."""
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
