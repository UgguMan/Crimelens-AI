"""
CrimeLens AI — Reports Router
=================================
API endpoints for investigation report generation and retrieval.
"""

from fastapi import APIRouter, Depends
from app.services.report_service import report_service
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/cases/{case_id}/generate")
async def generate_report(case_id: str, current_user: dict = Depends(get_current_user)):
    """Generate a comprehensive investigation report for a case."""
    result = await report_service.generate_report(case_id, current_user["user_id"])
    return {"success": True, "data": result, "message": "Report generated successfully."}


@router.get("/cases/{case_id}")
async def get_report(case_id: str, current_user: dict = Depends(get_current_user)):
    """Get the latest report for a case."""
    result = await report_service.get_report(case_id)
    if not result:
        return {"success": False, "message": "No report found. Generate one first."}
    return {"success": True, "data": result}
