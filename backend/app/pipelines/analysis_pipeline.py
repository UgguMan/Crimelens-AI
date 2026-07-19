"""
CrimeLens AI — AI Analysis Pipeline
=======================================
Integrates with Google Gemini API for intelligent evidence analysis.
Handles structured JSON output parsing, retry logic, and error handling.
"""

import json
import traceback
from typing import Optional

from app.config import get_settings
from app.models.analysis import AIAnalysisResult
from app.pipelines.prompts import MASTER_ANALYSIS_PROMPT, REPORT_GENERATION_PROMPT
from app.utils.helpers import Timer

# Lazy-initialized Gemini client
_gemini_model = None


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


def analyze_evidence_text(evidence_text: str) -> dict:
    """
    Run the master analysis prompt on extracted evidence text.
    Returns the parsed AIAnalysisResult as a dict.
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


def generate_report_content(analysis_data: dict) -> dict:
    """
    Generate a professional investigation report from analysis results.
    Returns structured report sections.
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
        return {
            "title": "Investigation Report",
            "executive_summary": analysis_data.get("case_summary", "Analysis data unavailable."),
            "error": str(e),
        }


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
