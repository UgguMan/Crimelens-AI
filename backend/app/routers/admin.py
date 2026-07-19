"""
CrimeLens AI — Admin Router
===============================
Admin-only API endpoints for user management and system monitoring.
Requires 'admin' role for all operations.
"""

from fastapi import APIRouter, Depends, Query

from app.middleware.auth import require_role
from app.repositories.user_repository import user_repository
from app.services.log_service import log_service
from app.models.user import UserUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: str | None = Query(None),
    current_user: dict = Depends(require_role("admin")),
):
    """List all users (admin only)."""
    skip = (page - 1) * page_size
    users = await user_repository.list_users(skip=skip, limit=page_size, role=role)
    # Strip password hashes
    for user in users:
        user.pop("password_hash", None)
    total = await user_repository.count()
    return {"success": True, "data": {"items": users, "total": total}}


@router.put("/users/{user_id}")
async def update_user(
    user_id: str, data: UserUpdate,
    current_user: dict = Depends(require_role("admin")),
):
    """Update a user's role or status (admin only)."""
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        return {"success": False, "message": "No fields to update."}
    await user_repository.update(user_id, update_data)
    await log_service.log_action(
        user_id=current_user["user_id"],
        action="admin.user_updated",
        resource_type="user",
        resource_id=user_id,
        details=update_data,
    )
    return {"success": True, "message": "User updated."}


@router.get("/logs")
async def get_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_role("admin")),
):
    """Get recent system activity logs (admin only)."""
    logs = await log_service.get_recent_activity(limit=limit)
    return {"success": True, "data": logs}


@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(require_role("admin"))):
    """Get system-wide statistics (admin only)."""
    user_counts = await user_repository.count_by_role()
    from app.repositories.case_repository import case_repository
    from app.repositories.evidence_repository import evidence_repository

    total_cases = await case_repository.count()
    total_evidence = await evidence_repository.count()
    status_stats = await case_repository.get_stats_by_status()

    return {
        "success": True,
        "data": {
            "users": user_counts,
            "total_users": sum(user_counts.values()),
            "total_cases": total_cases,
            "total_evidence": total_evidence,
            "cases_by_status": status_stats,
        },
    }
