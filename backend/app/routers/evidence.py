"""
CrimeLens AI — Evidence Router
==================================
API endpoints for evidence upload, retrieval, OCR results, and analysis.
"""

from fastapi import APIRouter, Depends, File, UploadFile

from app.services.evidence_service import evidence_service
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.post("/cases/{case_id}/upload")
async def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload a single evidence file to a case."""
    result = await evidence_service.upload_evidence(case_id, file, current_user["user_id"])
    return {"success": True, "data": result, "message": "Evidence uploaded and processed."}


@router.post("/cases/{case_id}/upload-multiple")
async def upload_multiple_evidence(
    case_id: str,
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload multiple evidence files to a case."""
    results = []
    for file in files:
        result = await evidence_service.upload_evidence(case_id, file, current_user["user_id"])
        results.append(result)
    return {"success": True, "data": results, "message": f"{len(results)} files uploaded."}


@router.get("/cases/{case_id}/list")
async def list_evidence(case_id: str, current_user: dict = Depends(get_current_user)):
    """Get all evidence files for a case."""
    evidence_list = await evidence_service.get_evidence_list(case_id)
    return {"success": True, "data": evidence_list}


@router.get("/{evidence_id}")
async def get_evidence(evidence_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single evidence file by ID."""
    result = await evidence_service.get_evidence(evidence_id)
    return {"success": True, "data": result}


@router.get("/{evidence_id}/ocr")
async def get_ocr_result(evidence_id: str, current_user: dict = Depends(get_current_user)):
    """Get OCR extraction results for an evidence file."""
    result = await evidence_service.get_ocr_result(evidence_id)
    return {"success": True, "data": result}


@router.get("/{evidence_id}/analysis")
async def get_analysis_result(evidence_id: str, current_user: dict = Depends(get_current_user)):
    """Get AI analysis results for an evidence file."""
    result = await evidence_service.get_analysis_result(evidence_id)
    return {"success": True, "data": result}


@router.post("/cases/{case_id}/analyze")
async def analyze_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Run comprehensive AI analysis on all evidence in a case."""
    result = await evidence_service.run_case_analysis(case_id, current_user["user_id"])
    return {"success": True, "data": result, "message": "Case analysis complete."}


@router.get("/cases/{case_id}/analysis")
async def get_case_analysis(case_id: str, current_user: dict = Depends(get_current_user)):
    """Get the case-level aggregated analysis."""
    result = await evidence_service.get_case_analysis(case_id)
    return {"success": True, "data": result}


@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an evidence file."""
    await evidence_service.delete_evidence(evidence_id, current_user["user_id"])
    return {"success": True, "message": "Evidence deleted."}
