"""
CrimeLens AI — Case Service
===============================
Business logic for investigation case lifecycle management.
"""

from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.models.case import CaseCreate, CaseUpdate, CaseInDB
from app.repositories.case_repository import case_repository
from app.services.log_service import log_service


class CaseService:
    """Manages case creation, updates, status transitions, and statistics."""

    def __init__(self):
        self.repo = case_repository

    async def create_case(self, data: CaseCreate, user_id: str) -> dict:
        """Create a new investigation case."""
        case_doc = CaseInDB(
            title=data.title,
            description=data.description,
            priority=data.priority,
            tags=CaseCreate.sanitize_tags(data.tags),
            created_by=user_id,
        ).model_dump()

        case_id = await self.repo.create(case_doc)

        await log_service.log_action(
            user_id=user_id,
            action="case.created",
            resource_type="case",
            resource_id=case_id,
            details={"title": data.title},
        )

        return await self.repo.find_by_id(case_id)

    async def get_case(self, case_id: str, user_id: str) -> dict:
        """Get a single case by ID with access check."""
        case = await self.repo.find_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
        return case

    async def list_cases(
        self, user_id: str, skip: int = 0, limit: int = 20,
        case_status: str | None = None, priority: str | None = None,
    ) -> dict:
        """List cases for a user with pagination and filters."""
        cases = await self.repo.find_by_user(
            user_id, skip=skip, limit=limit,
            status=case_status, priority=priority,
        )
        total = await self.repo.count_by_user(user_id)
        return {
            "items": cases,
            "total": total,
            "page": (skip // limit) + 1,
            "page_size": limit,
            "total_pages": (total + limit - 1) // limit,
        }

    async def update_case(self, case_id: str, data: CaseUpdate, user_id: str) -> dict:
        """Update case fields (partial update)."""
        case = await self.repo.find_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

        update_data = data.model_dump(exclude_none=True)
        if "tags" in update_data:
            update_data["tags"] = CaseCreate.sanitize_tags(update_data["tags"])
        update_data["updated_at"] = datetime.now(timezone.utc)

        await self.repo.update(case_id, update_data)

        await log_service.log_action(
            user_id=user_id,
            action="case.updated",
            resource_type="case",
            resource_id=case_id,
            details={"fields": list(update_data.keys())},
        )

        return await self.repo.find_by_id(case_id)

    async def delete_case(self, case_id: str, user_id: str) -> bool:
        """Delete a case and log the action."""
        case = await self.repo.find_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

        result = await self.repo.delete(case_id)

        await log_service.log_action(
            user_id=user_id,
            action="case.deleted",
            resource_type="case",
            resource_id=case_id,
            details={"title": case["title"]},
        )

        return result

    async def get_dashboard_stats(self, user_id: str) -> dict:
        """Get aggregate statistics for the dashboard."""
        status_stats = await self.repo.get_stats_by_status()
        priority_stats = await self.repo.get_stats_by_priority()
        total = await self.repo.count_by_user(user_id)

        return {
            "total_cases": total,
            "by_status": status_stats,
            "by_priority": priority_stats,
            "active_cases": status_stats.get("open", 0) + status_stats.get("in_progress", 0),
        }


# Singleton instance
case_service = CaseService()
