"""
CrimeLens AI — Evidence Repository
======================================
Data access layer for digital evidence and OCR results in MongoDB.
"""

from bson import ObjectId
from app.repositories.base import BaseRepository
from app.utils.helpers import serialize_doc


class EvidenceRepository(BaseRepository):
    """MongoDB operations for the 'evidence' collection."""

    collection_name = "evidence"

    async def find_by_case(self, case_id: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all evidence files for a case."""
        return await self.find_many({"case_id": case_id}, skip=skip, limit=limit)

    async def count_by_case(self, case_id: str) -> int:
        """Count evidence files in a case."""
        return await self.count({"case_id": case_id})

    async def update_ocr_status(self, evidence_id: str, status: str) -> bool:
        """Update the OCR processing status."""
        return await self.update(evidence_id, {"ocr_status": status})

    async def update_analysis_status(self, evidence_id: str, status: str) -> bool:
        """Update the AI analysis processing status."""
        return await self.update(evidence_id, {"analysis_status": status})

    async def get_pending_ocr(self, limit: int = 10) -> list[dict]:
        """Get evidence files pending OCR processing."""
        return await self.find_many({"ocr_status": "pending"}, limit=limit)

    async def get_pending_analysis(self, limit: int = 10) -> list[dict]:
        """Get evidence files pending AI analysis."""
        return await self.find_many(
            {"ocr_status": "completed", "analysis_status": "pending"},
            limit=limit,
        )


class OCRResultRepository(BaseRepository):
    """MongoDB operations for the 'ocr_results' collection."""

    collection_name = "ocr_results"

    async def find_by_evidence(self, evidence_id: str) -> dict | None:
        """Get OCR result for a specific evidence file."""
        return await self.find_one({"evidence_id": evidence_id})

    async def find_by_case(self, case_id: str) -> list[dict]:
        """Get all OCR results for evidence in a case (via join)."""
        pipeline = [
            {
                "$lookup": {
                    "from": "evidence",
                    "localField": "evidence_id",
                    "foreignField": "_id",
                    "as": "evidence_info",
                }
            },
            {"$unwind": {"path": "$evidence_info", "preserveNullAndEmptyArrays": True}},
            {"$match": {"evidence_info.case_id": case_id}},
            {"$sort": {"created_at": 1}},
        ]
        results = []
        db = self.collection.database
        async for doc in db.ocr_results.aggregate(pipeline):
            results.append(serialize_doc(doc))
        return results

    async def get_combined_text_for_case(self, case_id: str) -> str:
        """Get all OCR text for a case, concatenated with separators."""
        # First get all evidence IDs for this case
        evidence_cursor = self.collection.database.evidence.find(
            {"case_id": case_id}, {"_id": 1}
        )
        evidence_ids = [str(doc["_id"]) async for doc in evidence_cursor]

        if not evidence_ids:
            return ""

        # Get all OCR results for those evidence IDs
        ocr_cursor = self.collection.find(
            {"evidence_id": {"$in": evidence_ids}},
            {"full_text": 1, "evidence_id": 1},
        ).sort("created_at", 1)

        texts = []
        async for doc in ocr_cursor:
            if doc.get("full_text"):
                texts.append(f"--- Evidence: {doc['evidence_id']} ---\n{doc['full_text']}")

        return "\n\n".join(texts)


class AIReportRepository(BaseRepository):
    """MongoDB operations for the 'ai_reports' collection."""

    collection_name = "ai_reports"

    async def find_by_evidence(self, evidence_id: str) -> dict | None:
        """Get the AI analysis report for a specific evidence file."""
        return await self.find_one({"evidence_id": evidence_id, "analysis_type": "evidence"})

    async def find_by_case(self, case_id: str) -> dict | None:
        """Get the case-level AI analysis report."""
        return await self.find_one({"case_id": case_id, "analysis_type": "case"})

    async def find_all_for_case(self, case_id: str) -> list[dict]:
        """Get all AI reports (evidence + case level) for a case."""
        return await self.find_many({"case_id": case_id})


# Singleton instances
evidence_repository = EvidenceRepository()
ocr_result_repository = OCRResultRepository()
ai_report_repository = AIReportRepository()
