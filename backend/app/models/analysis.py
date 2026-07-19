"""
CrimeLens AI — AI Analysis Models
====================================
The core structured output schema that the Gemini LLM must produce.
Covers timeline events, entity extraction, suspicious patterns,
crime detection, risk scoring, and investigative recommendations.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.common import utc_now


class TimelineEvent(BaseModel):
    """A single chronological event extracted from evidence."""
    time: str = Field(..., description="Timestamp or relative time marker (e.g. '08:20 AM', 'March 15')")
    event: str = Field(..., description="Description of what occurred")
    event_type: str = Field(
        default="message",
        description="Category: message | transfer | threat | location | call | meeting | deletion | other",
    )
    source: str = Field(default="", description="Which evidence file this came from")
    severity: str = Field(default="low", description="low | medium | high | critical")


class SuspiciousMessage(BaseModel):
    """A flagged message with explanation of why it's suspicious."""
    message: str = Field(..., description="The suspicious text content")
    reason: str = Field(..., description="Detailed explanation of WHY this was flagged")
    category: str = Field(
        default="other",
        description="threat | blackmail | harassment | fraud | scam | identity_theft | manipulation | evidence_deletion | other",
    )
    severity: str = Field(default="medium", description="low | medium | high | critical")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class PossibleCrime(BaseModel):
    """A detected potential crime with supporting evidence."""
    crime: str = Field(..., description="Type/name of the possible crime")
    description: str = Field(default="", description="Detailed description of the crime pattern")
    evidence: str = Field(..., description="Specific evidence supporting this detection")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    legal_section: str = Field(default="", description="Relevant legal section if applicable")


class ExtractedEntities(BaseModel):
    """All entity types extracted from evidence text."""
    people: list[str] = Field(default_factory=list, description="Names of individuals mentioned")
    phone_numbers: list[str] = Field(default_factory=list, description="Phone numbers found")
    emails: list[str] = Field(default_factory=list, description="Email addresses found")
    locations: list[str] = Field(default_factory=list, description="Physical locations, addresses, cities, countries")
    organizations: list[str] = Field(default_factory=list, description="Organizations, companies, institutions")
    bank_accounts: list[str] = Field(default_factory=list, description="Bank account numbers or UPI IDs")
    vehicle_numbers: list[str] = Field(default_factory=list, description="Vehicle registration numbers")
    social_media_ids: list[str] = Field(default_factory=list, description="Social media handles/usernames")
    dates: list[str] = Field(default_factory=list, description="Dates and date ranges mentioned")
    times: list[str] = Field(default_factory=list, description="Specific times mentioned")
    addresses: list[str] = Field(default_factory=list, description="Full street/postal addresses")
    urls: list[str] = Field(default_factory=list, description="URLs and web links found")


class RelationshipNode(BaseModel):
    """A node in the relationship graph."""
    id: str
    label: str
    node_type: str = Field(description="person | organization | phone | location | email")
    metadata: dict = Field(default_factory=dict)


class RelationshipEdge(BaseModel):
    """An edge connecting two nodes in the relationship graph."""
    source: str
    target: str
    edge_type: str = Field(description="message | call | transfer | meeting | relationship")
    label: str = ""
    weight: float = 1.0


class RelationshipGraph(BaseModel):
    """Complete relationship graph extracted from evidence."""
    nodes: list[RelationshipNode] = Field(default_factory=list)
    edges: list[RelationshipEdge] = Field(default_factory=list)


class AIAnalysisResult(BaseModel):
    """
    Master analysis output schema.
    This is the EXACT structure that Gemini must return.
    Every field maps to a specific investigation concern.
    """
    case_summary: str = Field(default="", description="Executive summary of findings")
    timeline: list[TimelineEvent] = Field(default_factory=list, description="Chronological events")
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    suspicious_messages: list[SuspiciousMessage] = Field(default_factory=list)
    possible_crimes: list[PossibleCrime] = Field(default_factory=list)
    risk_score: int = Field(default=0, ge=0, le=100, description="Overall risk score 0-100")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Analysis confidence 0-1")
    recommendations: list[str] = Field(default_factory=list, description="Actionable next steps")
    conversation_summary: str = Field(default="", description="Summary of conversations detected")
    key_findings: list[str] = Field(default_factory=list, description="Top findings at a glance")
    relationship_graph: RelationshipGraph = Field(default_factory=RelationshipGraph)


class AIReportInDB(BaseModel):
    """Stored AI analysis report in MongoDB."""
    case_id: str
    evidence_id: Optional[str] = None
    analysis_type: str = Field(default="evidence", description="evidence | case")
    result: dict = Field(default_factory=dict)
    model_used: str = ""
    tokens_used: int = 0
    processing_time_ms: int = 0
    created_at: datetime = Field(default_factory=utc_now)
