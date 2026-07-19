"""
CrimeLens AI — Log Repository
=================================
Data access layer for activity logs in MongoDB.
"""

from app.repositories.base import BaseRepository


class LogRepository(BaseRepository):
    """MongoDB operations for the 'activity_logs' collection."""
    collection_name = "activity_logs"


# Singleton instance
log_repository = LogRepository()
