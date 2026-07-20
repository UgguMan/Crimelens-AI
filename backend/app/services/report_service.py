"""
CrimeLens AI — Report Service
=================================
Generates comprehensive investigation reports from case analysis data.
Handles edge cases like missing analysis, empty evidence, and Gemini failures.
"""

from app.models.common import utc_now
from app.repositories.evidence_repository import ai_report_repository, evidence_repository
from app.services.evidence_service import evidence_service
from app.pipelines.analysis_pipeline import generate_report_content
from app.services.log_service import log_service
from app.database import get_database
from fastapi import HTTPException, status


class ReportService:
    """Generates and manages investigation reports."""

    async def generate_report(self, case_id: str, user_id: str) -> dict:
        """Generate a comprehensive investigation report for a case."""
        # Get case analysis data
        analysis = await evidence_service.get_case_analysis(case_id)

        # If no case-level analysis exists, try to run it first
        if not analysis:
            try:
                analysis = await evidence_service.run_case_analysis(case_id, user_id)
            except HTTPException:
                pass  # Will be handled below

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No analysis data available. Upload evidence and run analysis first.",
            )

        # Get evidence list
        evidence_list = await evidence_service.get_evidence_list(case_id)

        # Generate report content via Gemini (with fallback)
        try:
            report_content = generate_report_content(analysis)
        except Exception as e:
            print(f"[CrimeLens] Report content generation failed: {e}")
            report_content = {
                "title": "Investigation Report",
                "executive_summary": analysis.get("case_summary", "Report generation encountered an issue."),
                "evidence_summary": f"{len(evidence_list)} evidence files were analyzed.",
                "timeline_narrative": "",
                "persons_of_interest": "",
                "risk_assessment": f"Risk Score: {analysis.get('risk_score', 0)}/100",
                "suspicious_findings": "",
                "recommendations": "\n".join(f"• {r}" for r in analysis.get("recommendations", [])),
                "conclusion": analysis.get("case_summary", ""),
            }

        # Build report sections
        sections = [
            {
                "title": "Executive Summary",
                "content": report_content.get("executive_summary", analysis.get("case_summary", "")),
                "section_type": "text",
            },
            {
                "title": "Evidence Summary",
                "content": report_content.get("evidence_summary", f"{len(evidence_list)} evidence files analyzed"),
                "section_type": "text",
            },
            {
                "title": "Timeline of Events",
                "content": report_content.get("timeline_narrative", ""),
                "section_type": "timeline",
                "data": analysis.get("timeline", []),
            },
            {
                "title": "Persons of Interest",
                "content": report_content.get("persons_of_interest", ""),
                "section_type": "entities",
                "data": analysis.get("entities", {}).get("people", []) if isinstance(analysis.get("entities"), dict) else [],
            },
            {
                "title": "Risk Assessment",
                "content": report_content.get("risk_assessment", ""),
                "section_type": "risk",
                "data": {
                    "risk_score": analysis.get("risk_score", 0),
                    "confidence": analysis.get("confidence_score", 0),
                },
            },
            {
                "title": "Suspicious Findings",
                "content": report_content.get("suspicious_findings", ""),
                "section_type": "table",
                "data": analysis.get("suspicious_messages", []),
            },
            {
                "title": "Possible Crimes",
                "content": "",
                "section_type": "table",
                "data": analysis.get("possible_crimes", []),
            },
            {
                "title": "Recommendations",
                "content": report_content.get("recommendations", ""),
                "section_type": "text",
                "data": analysis.get("recommendations", []),
            },
            {
                "title": "Conclusion",
                "content": report_content.get("conclusion", ""),
                "section_type": "text",
            },
            {
                "title": "Evidence Index",
                "content": "",
                "section_type": "table",
                "data": [
                    {
                        "filename": e.get("original_filename", ""),
                        "type": e.get("file_type", ""),
                        "status": e.get("analysis_status", ""),
                    }
                    for e in evidence_list
                ],
            },
        ]

        # Store report in DB
        report_doc = {
            "case_id": case_id,
            "title": report_content.get("title", "Investigation Report"),
            "sections": sections,
            "case_summary": analysis.get("case_summary", ""),
            "risk_score": analysis.get("risk_score"),
            "confidence_score": analysis.get("confidence_score"),
            "evidence_count": len(evidence_list),
            "entities_count": sum(
                len(v) for v in analysis.get("entities", {}).values()
                if isinstance(v, list)
            ) if isinstance(analysis.get("entities"), dict) else 0,
            "threats_count": len(analysis.get("suspicious_messages", [])),
            "generated_by": user_id,
            "generated_at": utc_now(),
        }

        db = get_database()
        result = await db.reports.insert_one(report_doc)
        report_doc["_id"] = str(result.inserted_id)

        await log_service.log_action(
            user_id=user_id,
            action="report.generated",
            resource_type="report",
            resource_id=str(result.inserted_id),
            details={"case_id": case_id},
        )

        return report_doc

    async def get_report(self, case_id: str) -> dict | None:
        """Get the latest report for a case."""
        db = get_database()
        from app.utils.helpers import serialize_doc
        doc = await db.reports.find_one(
            {"case_id": case_id},
            sort=[("generated_at", -1)],
        )
        return serialize_doc(doc) if doc else None


# Singleton instance
report_service = ReportService()
