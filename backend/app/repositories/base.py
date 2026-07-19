"""
CrimeLens AI — Base Repository
=================================
Abstract base class providing generic CRUD operations for MongoDB collections.
All domain-specific repositories inherit from this class.
"""

from typing import Any, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import get_database
from app.utils.helpers import serialize_doc


class BaseRepository:
    """
    Generic MongoDB repository with CRUD operations.
    Subclasses must set `collection_name` to the target MongoDB collection.
    """

    collection_name: str = ""

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the Motor collection for this repository."""
        db = get_database()
        return db[self.collection_name]

    async def create(self, document: dict) -> str:
        """
        Insert a new document.
        Returns the inserted document's ID as a string.
        """
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def find_by_id(self, doc_id: str) -> Optional[dict]:
        """Find a single document by its ObjectId."""
        if not ObjectId.is_valid(doc_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(doc_id)})
        return serialize_doc(doc) if doc else None

    async def find_one(self, query: dict) -> Optional[dict]:
        """Find a single document matching the query."""
        doc = await self.collection.find_one(query)
        return serialize_doc(doc) if doc else None

    async def find_many(
        self,
        query: dict,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: int = -1,
    ) -> list[dict]:
        """
        Find multiple documents with pagination and sorting.
        Returns a list of serialized documents.
        """
        cursor = (
            self.collection.find(query)
            .sort(sort_by, sort_order)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [serialize_doc(doc) for doc in docs]

    async def update(self, doc_id: str, update_data: dict) -> bool:
        """
        Update a document by ID.
        Returns True if a document was modified.
        """
        if not ObjectId.is_valid(doc_id):
            return False
        result = await self.collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": update_data},
        )
        return result.modified_count > 0

    async def delete(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        Returns True if a document was deleted.
        """
        if not ObjectId.is_valid(doc_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0

    async def count(self, query: dict | None = None) -> int:
        """Count documents matching the query (or all if no query)."""
        return await self.collection.count_documents(query or {})

    async def exists(self, query: dict) -> bool:
        """Check if any document matches the query."""
        doc = await self.collection.find_one(query, {"_id": 1})
        return doc is not None
