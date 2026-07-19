"""
CrimeLens AI — Report Models
===============================
Schemas for investigation report generation and PDF export.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.common import PyObjectId, utc_now


class ReportSection(BaseModel):
    """A single section within an investigation report."""
    title: str
    content: str = ""
    section_type: str = "text"  # text | timeline | entities | table | risk
    data: Optional[Any] = None


class ReportCreate(BaseModel):
    """Schema for triggering report generation."""
    title: str = Field(default="Investigation Report", max_length=200)
    include_timeline: bool = True
    include_entities: bool = True
    include_risk_analysis: bool = True
    include_evidence_index: bool = True
    include_recommendations: bool = True


class ReportResponse(BaseModel):
    """Generated report returned in API responses."""
    id: PyObjectId = Field(alias="_id")
    case_id: str
    title: str
    sections: list[ReportSection] = Field(default_factory=list)
    case_summary: str = ""
    risk_score: Optional[int] = None
    confidence_score: Optional[float] = None
    evidence_count: int = 0
    entities_count: int = 0
    threats_count: int = 0
    generated_by: str
    generated_at: datetime

    model_config = {"populate_by_name": True}


class ReportInDB(BaseModel):
    """Internal report representation stored in MongoDB."""
    case_id: str
    title: str = "Investigation Report"
    sections: list[dict] = Field(default_factory=list)
    case_summary: str = ""
    risk_score: Optional[int] = None
    confidence_score: Optional[float] = None
    evidence_count: int = 0
    entities_count: int = 0
    threats_count: int = 0
    generated_by: str
    generated_at: datetime = Field(default_factory=utc_now)
