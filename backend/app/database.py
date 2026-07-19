"""
CrimeLens AI — Database Connection Manager
============================================
Async MongoDB client using Motor driver.
Manages connection lifecycle, provides collection accessors,
and creates indexes on startup for optimal query performance.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

# Module-level client and database references
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_to_mongodb() -> None:
    """
    Initialize the Motor async client and verify connectivity.
    Called during FastAPI lifespan startup.
    """
    global _client, _database
    settings = get_settings()

    _client = AsyncIOMotorClient(
        settings.mongodb_uri,
        maxPoolSize=50,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000,
    )
    _database = _client[settings.db_name]

    # Verify connection is alive
    await _client.admin.command("ping")
    print(f"[CrimeLens] Connected to MongoDB: {settings.db_name}")

    # Create indexes for all collections
    await _create_indexes()


async def close_mongodb_connection() -> None:
    """
    Gracefully close the Motor client.
    Called during FastAPI lifespan shutdown.
    """
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        print("[CrimeLens] MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """
    Return the active database instance.
    Raises RuntimeError if called before connection is established.
    """
    if _database is None:
        raise RuntimeError(
            "Database not initialized. Ensure connect_to_mongodb() is called on startup."
        )
    return _database


async def _create_indexes() -> None:
    """
    Create MongoDB indexes for all collections.
    Indexes are idempotent — safe to call on every startup.
    """
    db = get_database()

    # Users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")

    # Cases collection
    await db.cases.create_index("created_by")
    await db.cases.create_index("assigned_to")
    await db.cases.create_index("status")
    await db.cases.create_index("priority")
    await db.cases.create_index([("title", "text"), ("description", "text")])
    await db.cases.create_index("created_at")

    # Evidence collection
    await db.evidence.create_index("case_id")
    await db.evidence.create_index("uploaded_by")
    await db.evidence.create_index("ocr_status")
    await db.evidence.create_index("analysis_status")

    # OCR Results collection
    await db.ocr_results.create_index("evidence_id", unique=True)

    # AI Reports collection
    await db.ai_reports.create_index("case_id")
    await db.ai_reports.create_index("evidence_id")

    # Search Embeddings collection
    await db.search_embeddings.create_index("case_id")
    await db.search_embeddings.create_index("evidence_id")

    # Activity Logs collection
    await db.activity_logs.create_index("user_id")
    await db.activity_logs.create_index("action")
    await db.activity_logs.create_index("created_at")

    print("[CrimeLens] Database indexes created.")
