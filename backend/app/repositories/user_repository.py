"""
CrimeLens AI — User Repository
==================================
Data access layer for user accounts in MongoDB.
"""

from typing import Optional
from bson import ObjectId
from app.repositories.base import BaseRepository
from app.utils.helpers import serialize_doc


class UserRepository(BaseRepository):
    """MongoDB operations for the 'users' collection."""

    collection_name = "users"

    async def find_by_email(self, email: str) -> Optional[dict]:
        """Find a user by their email address (case-insensitive)."""
        doc = await self.collection.find_one(
            {"email": email.lower().strip()}
        )
        return serialize_doc(doc) if doc else None

    async def create_user(self, user_data: dict) -> str:
        """
        Insert a new user document.
        Normalizes email to lowercase before storage.
        """
        user_data["email"] = user_data["email"].lower().strip()
        return await self.create(user_data)

    async def update_last_login(self, user_id: str, login_time) -> bool:
        """Record the user's last login timestamp."""
        return await self.update(user_id, {"last_login": login_time})

    async def list_users(
        self, skip: int = 0, limit: int = 20, role: str | None = None
    ) -> list[dict]:
        """List users with optional role filter and pagination."""
        query = {}
        if role:
            query["role"] = role
        return await self.find_many(query, skip=skip, limit=limit)

    async def deactivate_user(self, user_id: str) -> bool:
        """Soft-delete a user by setting is_active to False."""
        return await self.update(user_id, {"is_active": False})

    async def count_by_role(self) -> dict:
        """Get user count grouped by role."""
        pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        result = {}
        async for doc in self.collection.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        return result


# Singleton instance
user_repository = UserRepository()
