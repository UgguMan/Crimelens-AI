"""
CrimeLens AI — Analytics Router
===================================
API endpoints for dashboard analytics and data visualizations.
"""

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.repositories.case_repository import case_repository
from app.repositories.evidence_repository import evidence_repository
from app.database import get_database
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_overview(current_user: dict = Depends(get_current_user)):
    """Get high-level analytics overview for dashboard."""
    total_cases = await case_repository.count()
    total_evidence = await evidence_repository.count()
    status_stats = await case_repository.get_stats_by_status()
    priority_stats = await case_repository.get_stats_by_priority()

    # Count threats detected across all AI reports
    db = get_database()
    threats_pipeline = [
        {"$project": {"threat_count": {"$size": {"$ifNull": ["$result.suspicious_messages", []]}}}},
        {"$group": {"_id": None, "total": {"$sum": "$threat_count"}}},
    ]
    threats_result = await db.ai_reports.aggregate(threats_pipeline).to_list(1)
    total_threats = threats_result[0]["total"] if threats_result else 0

    return {
        "success": True,
        "data": {
            "total_cases": total_cases,
            "total_evidence": total_evidence,
            "total_threats": total_threats,
            "active_cases": status_stats.get("open", 0) + status_stats.get("in_progress", 0),
            "cases_by_status": status_stats,
            "cases_by_priority": priority_stats,
        },
    }


@router.get("/risk-distribution")
async def get_risk_distribution(current_user: dict = Depends(get_current_user)):
    """Get risk score distribution across cases."""
    distribution = await case_repository.get_risk_distribution()
    return {"success": True, "data": distribution}


@router.get("/recent-activity")
async def get_recent_activity(current_user: dict = Depends(get_current_user)):
    """Get recent system activity for the activity feed."""
    from app.services.log_service import log_service
    activity = await log_service.get_recent_activity(limit=30, user_id=current_user["user_id"])
    return {"success": True, "data": activity}


@router.get("/crime-types")
async def get_crime_type_distribution(current_user: dict = Depends(get_current_user)):
    """Get distribution of detected crime types."""
    db = get_database()
    pipeline = [
        {"$unwind": "$result.possible_crimes"},
        {"$group": {"_id": "$result.possible_crimes.crime", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    results = []
    async for doc in db.ai_reports.aggregate(pipeline):
        results.append({"crime": doc["_id"], "count": doc["count"]})
    return {"success": True, "data": results}
