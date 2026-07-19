"""
CrimeLens AI — Case Models
=============================
Pydantic schemas for case management lifecycle:
creation, updates, status transitions, and priority classification.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.common import PyObjectId, utc_now


class CaseStatus(str, Enum):
    """Investigation case lifecycle states."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CasePriority(str, Enum):
    """Case urgency classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CaseCreate(BaseModel):
    """Schema for creating a new investigation case."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(default="", max_length=5000)
    priority: CasePriority = Field(default=CasePriority.MEDIUM)
    tags: list[str] = Field(default_factory=list)

    @staticmethod
    def sanitize_tags(tags: list[str]) -> list[str]:
        """Normalize and deduplicate tags."""
        return list({tag.strip().lower() for tag in tags if tag.strip()})


class CaseUpdate(BaseModel):
    """Schema for partial case updates."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    assigned_to: Optional[str] = None
    tags: Optional[list[str]] = None


class CaseResponse(BaseModel):
    """Case data returned in API responses."""
    id: PyObjectId = Field(alias="_id")
    title: str
    description: str = ""
    status: CaseStatus = CaseStatus.OPEN
    priority: CasePriority = CasePriority.MEDIUM
    assigned_to: Optional[str] = None
    created_by: str
    tags: list[str] = Field(default_factory=list)
    evidence_count: int = 0
    risk_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True}


class CaseInDB(BaseModel):
    """Internal case representation stored in MongoDB."""
    title: str
    description: str = ""
    status: CaseStatus = CaseStatus.OPEN
    priority: CasePriority = CasePriority.MEDIUM
    assigned_to: Optional[str] = None
    created_by: str  # User ObjectId as string
    tags: list[str] = Field(default_factory=list)
    evidence_count: int = 0
    ai_analysis: Optional[dict[str, Any]] = None
    risk_score: Optional[int] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CaseStats(BaseModel):
    """Aggregated statistics for a case."""
    total_evidence: int = 0
    ocr_completed: int = 0
    analysis_completed: int = 0
    entities_found: int = 0
    threats_detected: int = 0
    risk_score: Optional[int] = None
