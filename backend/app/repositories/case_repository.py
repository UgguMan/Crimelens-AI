"""
CrimeLens AI — Case Repository
==================================
Data access layer for investigation cases in MongoDB.
"""

from bson import ObjectId
from app.repositories.base import BaseRepository
from app.utils.helpers import serialize_doc


class CaseRepository(BaseRepository):
    """MongoDB operations for the 'cases' collection."""

    collection_name = "cases"

    async def find_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20,
        status: str | None = None, priority: str | None = None,
    ) -> list[dict]:
        """Find cases created by or assigned to a user with optional filters."""
        query = {
            "$or": [
                {"created_by": user_id},
                {"assigned_to": user_id},
            ]
        }
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        return await self.find_many(query, skip=skip, limit=limit)

    async def count_by_user(self, user_id: str) -> int:
        """Count cases accessible to a user."""
        return await self.count({
            "$or": [
                {"created_by": user_id},
                {"assigned_to": user_id},
            ]
        })

    async def search_cases(self, search_term: str, user_id: str, limit: int = 20) -> list[dict]:
        """Full-text search on case title and description."""
        query = {
            "$text": {"$search": search_term},
            "$or": [
                {"created_by": user_id},
                {"assigned_to": user_id},
            ]
        }
        cursor = self.collection.find(
            query,
            {"score": {"$meta": "textScore"}},
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [serialize_doc(doc) for doc in docs]

    async def increment_evidence_count(self, case_id: str, delta: int = 1) -> bool:
        """Increment or decrement the evidence_count field."""
        result = await self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {"$inc": {"evidence_count": delta}},
        )
        return result.modified_count > 0

    async def get_stats_by_status(self) -> dict:
        """Get case count grouped by status."""
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        result = {}
        async for doc in self.collection.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result

    async def get_stats_by_priority(self) -> dict:
        """Get case count grouped by priority."""
        pipeline = [
            {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
        ]
        result = {}
        async for doc in self.collection.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result

    async def get_risk_distribution(self) -> list[dict]:
        """Get distribution of risk scores across cases."""
        pipeline = [
            {"$match": {"risk_score": {"$ne": None}}},
            {
                "$bucket": {
                    "groupBy": "$risk_score",
                    "boundaries": [0, 20, 40, 60, 80, 101],
                    "default": "unknown",
                    "output": {"count": {"$sum": 1}},
                }
            },
        ]
        results = []
        async for doc in self.collection.aggregate(pipeline):
            results.append(serialize_doc(doc))
        return results


# Singleton instance
case_repository = CaseRepository()
