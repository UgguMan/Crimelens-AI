"""
CrimeLens AI — Evidence Models
=================================
Pydantic schemas for digital evidence management:
file uploads, OCR processing status, and analysis tracking.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.models.common import PyObjectId, utc_now


class FileType(str, Enum):
    """Supported evidence file categories."""
    IMAGE = "image"
    PDF = "pdf"
    TEXT = "text"
    CSV = "csv"
    EMAIL = "email"
    DOCUMENT = "document"


class ProcessingStatus(str, Enum):
    """Pipeline processing states for OCR and AI analysis."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceResponse(BaseModel):
    """Evidence metadata returned in API responses."""
    id: PyObjectId = Field(alias="_id")
    case_id: str
    filename: str
    original_filename: str
    file_type: FileType
    mime_type: str
    file_size: int
    ocr_status: ProcessingStatus = ProcessingStatus.PENDING
    analysis_status: ProcessingStatus = ProcessingStatus.PENDING
    uploaded_by: str
    created_at: datetime

    model_config = {"populate_by_name": True}


class EvidenceInDB(BaseModel):
    """Internal evidence representation stored in MongoDB."""
    case_id: str
    filename: str  # UUID-based stored filename
    original_filename: str  # User's original filename
    file_type: FileType
    mime_type: str
    file_size: int  # bytes
    upload_path: str  # Relative path within upload directory
    ocr_status: ProcessingStatus = ProcessingStatus.PENDING
    analysis_status: ProcessingStatus = ProcessingStatus.PENDING
    uploaded_by: str  # User ObjectId as string
    created_at: datetime = Field(default_factory=utc_now)


class OCRTextBlock(BaseModel):
    """Single block of OCR-detected text with position and confidence."""
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: list[list[int]] = Field(default_factory=list)
    line_number: int = 0


class OCRResult(BaseModel):
    """Complete OCR extraction result for a single evidence file."""
    evidence_id: str
    full_text: str = ""
    text_blocks: list[OCRTextBlock] = Field(default_factory=list)
    language: str = "en"
    processing_time_ms: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class EvidenceWithOCR(BaseModel):
    """Combined evidence metadata and OCR result for API responses."""
    evidence: EvidenceResponse
    ocr_result: Optional[OCRResult] = None
    analysis: Optional[dict[str, Any]] = None
