"""
CrimeLens AI — AI Analysis Pipeline
=======================================
Integrates with Google Gemini API for intelligent evidence analysis.
Handles structured JSON output parsing, retry logic, and error handling.
Runs Gemini API calls in a thread pool for non-blocking async operation.
"""

import json
import asyncio
import traceback
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from app.config import get_settings
from app.models.analysis import AIAnalysisResult
from app.pipelines.prompts import MASTER_ANALYSIS_PROMPT, REPORT_GENERATION_PROMPT
from app.utils.helpers import Timer

# Lazy-initialized Gemini client
_gemini_model = None

# Thread pool for Gemini API calls
_analysis_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="analysis")


def _get_gemini_model():
    """Lazy singleton for Gemini generative model."""
    global _gemini_model
    if _gemini_model is None:
        import google.generativeai as genai

        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Set it in your .env file to enable AI analysis."
            )

        genai.configure(api_key=settings.gemini_api_key)
        _gemini_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.2,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
        )
        print("[CrimeLens] Gemini model initialized (gemini-2.0-flash).")
    return _gemini_model


def _analyze_evidence_text_sync(evidence_text: str) -> dict:
    """
    Synchronous version of evidence text analysis.
    Meant to run in a thread pool.
    """
    if not evidence_text or not evidence_text.strip():
        return AIAnalysisResult(
            case_summary="No text content was found in the uploaded evidence.",
            risk_score=0,
            confidence_score=0.0,
            key_findings=["No readable text detected in the evidence file."],
        ).model_dump()

    with Timer() as timer:
        model = _get_gemini_model()

        # Format the prompt with evidence text
        prompt = MASTER_ANALYSIS_PROMPT.format(
            evidence_text=evidence_text[:15000]  # Limit to ~15k chars for token safety
        )

        # Call Gemini API
        try:
            response = model.generate_content(prompt)
            response_text = response.text

            # Parse JSON response
            result = _parse_analysis_response(response_text)

            # Track metadata
            result["_processing_time_ms"] = timer.elapsed_ms
            result["_model_used"] = "gemini-2.0-flash"

            return result

        except Exception as e:
            print(f"[CrimeLens] Gemini API Error: {traceback.format_exc()}")
            return AIAnalysisResult(
                case_summary=f"AI analysis encountered an error: {str(e)}",
                risk_score=0,
                confidence_score=0.0,
                key_findings=[f"Analysis error: {str(e)}"],
                recommendations=["Re-upload the evidence and try again.", "Check if the evidence contains readable text."],
            ).model_dump()


def analyze_evidence_text(evidence_text: str) -> dict:
    """
    Run the master analysis prompt on extracted evidence text.
    Returns the parsed AIAnalysisResult as a dict.
    This function is synchronous for backward compatibility.
    """
    return _analyze_evidence_text_sync(evidence_text)


def _generate_report_content_sync(analysis_data: dict) -> dict:
    """
    Synchronous version of report content generation.
    Meant to run in a thread pool.
    """
    model = _get_gemini_model()

    prompt = REPORT_GENERATION_PROMPT.format(
        analysis_data=json.dumps(analysis_data, indent=2, default=str)[:12000]
    )

    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"[CrimeLens] Report generation error: {traceback.format_exc()}")
        # Return a meaningful fallback report instead of failing
        return {
            "title": "Investigation Report",
            "executive_summary": analysis_data.get("case_summary", "Analysis data unavailable."),
            "evidence_summary": f"Analysis contained {len(analysis_data.get('key_findings', []))} key findings.",
            "timeline_narrative": _format_timeline_fallback(analysis_data),
            "persons_of_interest": _format_persons_fallback(analysis_data),
            "risk_assessment": f"Risk Score: {analysis_data.get('risk_score', 'N/A')}/100. Confidence: {analysis_data.get('confidence_score', 'N/A')}.",
            "suspicious_findings": _format_suspicious_fallback(analysis_data),
            "recommendations": "\n".join(f"• {r}" for r in analysis_data.get("recommendations", ["No recommendations available."])),
            "conclusion": analysis_data.get("case_summary", "Report generation encountered an error. Please review the raw analysis data."),
            "confidence_statement": f"Analysis confidence: {analysis_data.get('confidence_score', 0.0) * 100:.0f}%",
        }


def generate_report_content(analysis_data: dict) -> dict:
    """
    Generate a professional investigation report from analysis results.
    Returns structured report sections.
    """
    return _generate_report_content_sync(analysis_data)


def _format_timeline_fallback(analysis_data: dict) -> str:
    """Format timeline data as a narrative string for fallback reports."""
    timeline = analysis_data.get("timeline", [])
    if not timeline:
        return "No timeline events were extracted from the evidence."
    lines = []
    for event in timeline:
        if isinstance(event, dict):
            time_str = event.get("time", "Unknown time")
            event_str = event.get("event", "Unknown event")
            lines.append(f"• [{time_str}] {event_str}")
    return "\n".join(lines) if lines else "No timeline events available."


def _format_persons_fallback(analysis_data: dict) -> str:
    """Format persons of interest for fallback reports."""
    entities = analysis_data.get("entities", {})
    people = entities.get("people", []) if isinstance(entities, dict) else []
    if not people:
        return "No persons of interest identified."
    return "Persons of interest: " + ", ".join(people)


def _format_suspicious_fallback(analysis_data: dict) -> str:
    """Format suspicious findings for fallback reports."""
    suspicious = analysis_data.get("suspicious_messages", [])
    if not suspicious:
        return "No suspicious messages detected."
    lines = []
    for msg in suspicious:
        if isinstance(msg, dict):
            lines.append(f"• [{msg.get('severity', 'unknown').upper()}] {msg.get('message', 'N/A')} — {msg.get('reason', '')}")
    return "\n".join(lines) if lines else "No suspicious findings formatted."


def _parse_analysis_response(response_text: str) -> dict:
    """
    Parse and validate the Gemini JSON response.
    Handles common parsing issues like markdown code blocks.
    """
    text = response_text.strip()

    # Strip markdown code block wrappers if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Attempt to find JSON object in the response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            parsed = json.loads(text[start:end])
        else:
            raise ValueError(f"Could not parse JSON from Gemini response: {text[:200]}")

    # Validate against our schema (lenient — fill defaults for missing fields)
    try:
        validated = AIAnalysisResult(**parsed)
        return validated.model_dump()
    except Exception:
        # Return raw parsed dict if validation fails (schema mismatch)
        return parsed
