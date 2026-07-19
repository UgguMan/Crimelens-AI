"""
CrimeLens AI — Search Router
================================
API endpoints for semantic and keyword search across case evidence.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.services.search_service import search_service
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])


class SearchQuery(BaseModel):
    """Search request body."""
    query: str = Field(..., min_length=1, max_length=500)


@router.post("/cases/{case_id}")
async def search_case(
    case_id: str, body: SearchQuery, current_user: dict = Depends(get_current_user),
):
    """Search evidence in a case using natural language queries."""
    result = await search_service.search_case(case_id, body.query)
    return {"success": True, "data": result}
