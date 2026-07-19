"""
CrimeLens AI — Activity Log Service
======================================
Logs all significant user actions for audit trail and activity feed.
"""

from datetime import datetime, timezone
from app.repositories.log_repository import log_repository


class LogService:
    """Records and queries user activity logs."""

    def __init__(self):
        self.repo = log_repository

    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str = "",
        resource_id: str = "",
        details: dict | None = None,
        ip_address: str = "",
    ) -> str:
        """
        Record an activity log entry.
        Returns the log entry ID.
        """
        log_doc = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc),
        }
        return await self.repo.create(log_doc)

    async def get_recent_activity(
        self, limit: int = 20, user_id: str | None = None
    ) -> list[dict]:
        """Get recent activity logs, optionally filtered by user."""
        query = {}
        if user_id:
            query["user_id"] = user_id
        return await self.repo.find_many(query, limit=limit)

    async def get_activity_by_resource(
        self, resource_type: str, resource_id: str, limit: int = 50
    ) -> list[dict]:
        """Get all activity for a specific resource."""
        query = {"resource_type": resource_type, "resource_id": resource_id}
        return await self.repo.find_many(query, limit=limit)


# Singleton instance
log_service = LogService()
