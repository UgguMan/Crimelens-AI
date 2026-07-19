"""
CrimeLens AI — Cases Router
===============================
RESTful API endpoints for investigation case management.
"""

from fastapi import APIRouter, Depends, Query

from app.services.case_service import case_service
from app.middleware.auth import get_current_user
from app.models.case import CaseCreate, CaseUpdate

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("")
async def create_case(data: CaseCreate, current_user: dict = Depends(get_current_user)):
    """Create a new investigation case."""
    result = await case_service.create_case(data, current_user["user_id"])
    return {"success": True, "data": result}


@router.get("")
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """List cases with pagination and filters."""
    skip = (page - 1) * page_size
    result = await case_service.list_cases(
        current_user["user_id"], skip=skip, limit=page_size,
        case_status=status, priority=priority,
    )
    return {"success": True, "data": result}


@router.get("/stats")
async def get_case_stats(current_user: dict = Depends(get_current_user)):
    """Get aggregate case statistics for dashboard."""
    stats = await case_service.get_dashboard_stats(current_user["user_id"])
    return {"success": True, "data": stats}


@router.get("/{case_id}")
async def get_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single case by ID."""
    result = await case_service.get_case(case_id, current_user["user_id"])
    return {"success": True, "data": result}


@router.put("/{case_id}")
async def update_case(
    case_id: str, data: CaseUpdate, current_user: dict = Depends(get_current_user),
):
    """Update case details."""
    result = await case_service.update_case(case_id, data, current_user["user_id"])
    return {"success": True, "data": result}


@router.delete("/{case_id}")
async def delete_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a case."""
    await case_service.delete_case(case_id, current_user["user_id"])
    return {"success": True, "message": "Case deleted successfully."}
