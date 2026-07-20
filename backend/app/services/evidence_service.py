"""
CrimeLens AI — Evidence Service
===================================
Business logic for evidence upload, OCR processing, and AI analysis triggering.
Orchestrates the complete evidence processing pipeline.
"""

import aiofiles
from pathlib import Path
from fastapi import HTTPException, UploadFile, status

from app.config import get_settings
from app.models.evidence import EvidenceInDB, ProcessingStatus
from app.repositories.evidence_repository import (
    evidence_repository,
    ocr_result_repository,
    ai_report_repository,
)
from app.repositories.case_repository import case_repository
from app.services.log_service import log_service
from app.pipelines.ocr_pipeline import process_evidence
from app.pipelines.analysis_pipeline import analyze_evidence_text
from app.utils.file_validator import validate_upload, FileValidationError


class EvidenceService:
    """Manages evidence uploads, OCR processing, and AI analysis."""

    def __init__(self):
        self.evidence_repo = evidence_repository
        self.ocr_repo = ocr_result_repository
        self.ai_repo = ai_report_repository
        self.case_repo = case_repository

    async def upload_evidence(
        self, case_id: str, file: UploadFile, user_id: str
    ) -> dict:
        """
        Upload and process a single evidence file:
        1. Validate the file
        2. Save to disk
        3. Create DB record
        4. Run OCR
        5. Run AI analysis
        6. Store results
        """
        # Verify case exists
        case = await self.case_repo.find_by_id(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Validate upload
        try:
            stored_name, cleaned_name, file_type = validate_upload(
                filename=file.filename or "unknown",
                mime_type=file.content_type or "application/octet-stream",
                file_size=file_size,
            )
        except FileValidationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # Save file to disk
        settings = get_settings()
        case_upload_dir = settings.upload_path / case_id
        case_upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = case_upload_dir / stored_name

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        # Create evidence record in DB
        evidence_doc = EvidenceInDB(
            case_id=case_id,
            filename=stored_name,
            original_filename=cleaned_name,
            file_type=file_type,
            mime_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            upload_path=str(file_path),
            uploaded_by=user_id,
        ).model_dump()

        evidence_id = await self.evidence_repo.create(evidence_doc)

        # Update case evidence count
        await self.case_repo.increment_evidence_count(case_id)

        # Log the upload
        await log_service.log_action(
            user_id=user_id,
            action="evidence.uploaded",
            resource_type="evidence",
            resource_id=evidence_id,
            details={"filename": cleaned_name, "case_id": case_id, "file_type": file_type},
        )

        # --- Run OCR Pipeline ---
        await self.evidence_repo.update_ocr_status(evidence_id, ProcessingStatus.PROCESSING.value)
        try:
            ocr_result = await process_evidence(str(file_path), file_type, evidence_id)
            ocr_doc = ocr_result.model_dump()
            await self.ocr_repo.create(ocr_doc)
            await self.evidence_repo.update_ocr_status(evidence_id, ProcessingStatus.COMPLETED.value)
        except Exception as e:
            await self.evidence_repo.update_ocr_status(evidence_id, ProcessingStatus.FAILED.value)
            print(f"[CrimeLens] OCR failed for {evidence_id}: {e}")
            return await self.evidence_repo.find_by_id(evidence_id)

        # --- Run AI Analysis Pipeline ---
        await self.evidence_repo.update_analysis_status(evidence_id, ProcessingStatus.PROCESSING.value)
        try:
            analysis_result = analyze_evidence_text(ocr_result.full_text)

            ai_doc = {
                "case_id": case_id,
                "evidence_id": evidence_id,
                "analysis_type": "evidence",
                "result": analysis_result,
                "model_used": analysis_result.pop("_model_used", "gemini-2.0-flash"),
                "processing_time_ms": analysis_result.pop("_processing_time_ms", 0),
            }
            from app.models.common import utc_now
            ai_doc["created_at"] = utc_now()

            await self.ai_repo.create(ai_doc)
            await self.evidence_repo.update_analysis_status(evidence_id, ProcessingStatus.COMPLETED.value)

            # Update case risk score if this analysis has one
            risk_score = analysis_result.get("risk_score")
            if risk_score is not None:
                await self.case_repo.update(case_id, {"risk_score": risk_score})

        except Exception as e:
            await self.evidence_repo.update_analysis_status(evidence_id, ProcessingStatus.FAILED.value)
            print(f"[CrimeLens] AI analysis failed for {evidence_id}: {e}")

        return await self.evidence_repo.find_by_id(evidence_id)

    async def get_evidence_list(self, case_id: str) -> list[dict]:
        """Get all evidence for a case."""
        return await self.evidence_repo.find_by_case(case_id)

    async def get_evidence(self, evidence_id: str) -> dict:
        """Get a single evidence file by ID."""
        evidence = await self.evidence_repo.find_by_id(evidence_id)
        if not evidence:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found.")
        return evidence

    async def get_ocr_result(self, evidence_id: str) -> dict | None:
        """Get OCR result for an evidence file."""
        return await self.ocr_repo.find_by_evidence(evidence_id)

    async def get_analysis_result(self, evidence_id: str) -> dict | None:
        """Get AI analysis result for an evidence file."""
        report = await self.ai_repo.find_by_evidence(evidence_id)
        if report:
            return report.get("result", {})
        return None

    async def get_case_analysis(self, case_id: str) -> dict | None:
        """Get the case-level aggregated analysis."""
        report = await self.ai_repo.find_by_case(case_id)
        if report:
            return report.get("result", {})

        # If no case-level report, aggregate from evidence-level reports
        all_reports = await self.ai_repo.find_all_for_case(case_id)
        if not all_reports:
            return None

        return self._aggregate_reports(all_reports)

    async def run_case_analysis(self, case_id: str, user_id: str) -> dict:
        """Run a comprehensive case-level analysis combining all evidence."""
        # Get all OCR text for the case
        combined_text = await self.ocr_repo.get_combined_text_for_case(case_id)
        if not combined_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No OCR text available. Upload and process evidence first.",
            )

        # Run analysis
        analysis_result = analyze_evidence_text(combined_text)

        # Store case-level report
        from app.models.common import utc_now
        ai_doc = {
            "case_id": case_id,
            "evidence_id": None,
            "analysis_type": "case",
            "result": analysis_result,
            "model_used": analysis_result.pop("_model_used", "gemini-2.0-flash"),
            "processing_time_ms": analysis_result.pop("_processing_time_ms", 0),
            "created_at": utc_now(),
        }
        await self.ai_repo.create(ai_doc)

        # Update case risk score
        risk_score = analysis_result.get("risk_score")
        if risk_score is not None:
            await self.case_repo.update(case_id, {
                "risk_score": risk_score,
                "ai_analysis": analysis_result,
            })

        await log_service.log_action(
            user_id=user_id,
            action="case.analyzed",
            resource_type="case",
            resource_id=case_id,
        )

        return analysis_result

    async def delete_evidence(self, evidence_id: str, user_id: str) -> bool:
        """Delete evidence and its associated OCR/analysis data."""
        evidence = await self.evidence_repo.find_by_id(evidence_id)
        if not evidence:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found.")

        # Delete file from disk
        file_path = Path(evidence.get("upload_path", ""))
        if file_path.exists():
            file_path.unlink()

        # Delete DB records
        await self.evidence_repo.delete(evidence_id)
        await self.case_repo.increment_evidence_count(evidence["case_id"], delta=-1)

        await log_service.log_action(
            user_id=user_id,
            action="evidence.deleted",
            resource_type="evidence",
            resource_id=evidence_id,
        )

        return True

    def _aggregate_reports(self, reports: list[dict]) -> dict:
        """Combine multiple evidence-level reports into a case summary."""
        combined = {
            "case_summary": "",
            "timeline": [],
            "entities": {"people": [], "phone_numbers": [], "emails": [],
                        "locations": [], "organizations": [], "bank_accounts": [],
                        "vehicle_numbers": [], "social_media_ids": [], "dates": [],
                        "times": [], "addresses": [], "urls": []},
            "suspicious_messages": [],
            "possible_crimes": [],
            "risk_score": 0,
            "confidence_score": 0.0,
            "recommendations": [],
            "key_findings": [],
            "relationship_graph": {"nodes": [], "edges": []},
        }

        risk_scores = []
        confidence_scores = []

        for report in reports:
            result = report.get("result", {})

            # Merge timelines
            combined["timeline"].extend(result.get("timeline", []))

            # Merge entities (deduplicate)
            entities = result.get("entities", {})
            for key in combined["entities"]:
                existing = set(combined["entities"][key])
                existing.update(entities.get(key, []))
                combined["entities"][key] = list(existing)

            # Merge suspicious messages and crimes
            combined["suspicious_messages"].extend(result.get("suspicious_messages", []))
            combined["possible_crimes"].extend(result.get("possible_crimes", []))
            combined["recommendations"].extend(result.get("recommendations", []))
            combined["key_findings"].extend(result.get("key_findings", []))

            # Merge graph
            graph = result.get("relationship_graph", {})
            combined["relationship_graph"]["nodes"].extend(graph.get("nodes", []))
            combined["relationship_graph"]["edges"].extend(graph.get("edges", []))

            if result.get("risk_score"):
                risk_scores.append(result["risk_score"])
            if result.get("confidence_score"):
                confidence_scores.append(result["confidence_score"])

        # Calculate aggregate scores
        combined["risk_score"] = int(max(risk_scores)) if risk_scores else 0
        combined["confidence_score"] = round(
            sum(confidence_scores) / len(confidence_scores), 2
        ) if confidence_scores else 0.0

        # Deduplicate recommendations
        combined["recommendations"] = list(set(combined["recommendations"]))
        combined["key_findings"] = list(set(combined["key_findings"]))

        return combined


# Singleton instance
evidence_service = EvidenceService()
