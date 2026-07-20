"""
CrimeLens AI — OCR Pipeline
===============================
Extracts text from uploaded evidence files using Google Gemini Vision API.
This approach uses ZERO server memory for OCR (unlike EasyOCR which needs ~400MB).
Handles images, PDFs, and text-based files with unified output.
"""

import io
import csv
import base64
import json
import traceback
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.models.evidence import OCRResult, OCRTextBlock
from app.utils.helpers import Timer


def _get_gemini_vision_model():
    """Get a Gemini model configured for OCR/vision tasks."""
    import google.generativeai as genai

    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config={
            "temperature": 0.1,
            "max_output_tokens": 8192,
        },
    )
    return model


OCR_VISION_PROMPT = """You are a precise OCR engine. Extract ALL text from this image exactly as it appears.

RULES:
1. Extract every single piece of text visible in the image
2. Preserve the original layout, line breaks, and formatting as much as possible
3. If this is a chat/messaging screenshot, format as: [timestamp] Sender: Message
4. If this is a document, preserve headings, paragraphs, and structure
5. Include ALL numbers, dates, phone numbers, emails, URLs, and special characters
6. Do NOT summarize or interpret — extract text EXACTLY as shown
7. If text is partially visible or blurry, extract what you can and mark unclear parts with [unclear]
8. Return ONLY the extracted text, nothing else — no explanations or commentary"""


def process_image_with_gemini(file_path: str) -> OCRResult:
    """
    Extract text from an image using Gemini Vision API.
    Zero server memory overhead — all processing happens via API.
    """
    with Timer() as timer:
        model = _get_gemini_vision_model()

        # Read and encode the image
        image_path = Path(file_path)
        image_bytes = image_path.read_bytes()

        # Determine MIME type
        suffix = image_path.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif",
            ".webp": "image/webp", ".bmp": "image/bmp",
            ".tiff": "image/tiff", ".tif": "image/tiff",
        }
        mime_type = mime_map.get(suffix, "image/jpeg")

        # Send to Gemini Vision
        import google.generativeai as genai
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes,
        }

        response = model.generate_content([OCR_VISION_PROMPT, image_part])
        extracted_text = response.text.strip()

    text_blocks = []
    if extracted_text:
        lines = extracted_text.split("\n")
        for idx, line in enumerate(lines):
            if line.strip():
                text_blocks.append(OCRTextBlock(
                    text=line.strip(),
                    confidence=0.95,
                    line_number=idx + 1,
                ))

    return OCRResult(
        evidence_id="",
        full_text=extracted_text,
        text_blocks=text_blocks,
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


def process_pdf(file_path: str) -> OCRResult:
    """
    Extract text from a PDF file.
    Uses PyPDF2 for text-based PDFs, falls back to Gemini Vision for scanned pages.
    """
    from PyPDF2 import PdfReader

    with Timer() as timer:
        reader = PdfReader(file_path)
        all_text_parts = []
        text_blocks = []
        line_counter = 0

        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""

            if page_text.strip():
                # Text-based PDF page
                all_text_parts.append(f"[Page {page_num + 1}]\n{page_text.strip()}")
                line_counter += 1
                text_blocks.append(OCRTextBlock(
                    text=page_text.strip(),
                    confidence=0.95,
                    line_number=line_counter,
                ))
            else:
                # Scanned page — try to extract images and OCR via Gemini
                ocr_text = _ocr_pdf_page_images(page, page_num)
                if ocr_text:
                    all_text_parts.append(f"[Page {page_num + 1}]\n{ocr_text}")
                    line_counter += 1
                    text_blocks.append(OCRTextBlock(
                        text=ocr_text,
                        confidence=0.85,
                        line_number=line_counter,
                    ))
                else:
                    all_text_parts.append(f"[Page {page_num + 1}] (scanned — no extractable text)")

    return OCRResult(
        evidence_id="",
        full_text="\n\n".join(all_text_parts),
        text_blocks=text_blocks,
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


def _ocr_pdf_page_images(page, page_num: int) -> str:
    """Try to extract images from a PDF page and OCR them via Gemini."""
    try:
        if not hasattr(page, 'images') or not page.images:
            return ""

        all_text = []
        model = _get_gemini_vision_model()

        for img_idx, image in enumerate(page.images):
            try:
                image_bytes = image.data
                if image_bytes and len(image_bytes) > 500:
                    import google.generativeai as genai
                    image_part = {
                        "mime_type": "image/png",
                        "data": image_bytes,
                    }
                    response = model.generate_content([OCR_VISION_PROMPT, image_part])
                    text = response.text.strip()
                    if text:
                        all_text.append(text)
            except Exception:
                continue

        return "\n".join(all_text) if all_text else ""
    except Exception:
        return ""


def process_text_file(file_path: str) -> OCRResult:
    """Read plain text files directly."""
    with Timer() as timer:
        path = Path(file_path)
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="latin-1")

    return OCRResult(
        evidence_id="",
        full_text=content,
        text_blocks=[OCRTextBlock(text=content, confidence=1.0, line_number=1)],
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


def process_csv_file(file_path: str) -> OCRResult:
    """Parse CSV files into structured text."""
    with Timer() as timer:
        path = Path(file_path)
        try:
            raw_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_text = path.read_text(encoding="latin-1")

        text_lines = []
        csv_reader = csv.reader(io.StringIO(raw_text))
        headers = None

        for row_idx, row in enumerate(csv_reader):
            if row_idx == 0:
                headers = row
                text_lines.append("Headers: " + " | ".join(row))
            else:
                if headers:
                    row_text = " | ".join(
                        f"{headers[i] if i < len(headers) else 'col' + str(i)}: {val}"
                        for i, val in enumerate(row)
                    )
                else:
                    row_text = " | ".join(row)
                text_lines.append(f"Row {row_idx}: {row_text}")

    full_text = "\n".join(text_lines)
    return OCRResult(
        evidence_id="",
        full_text=full_text,
        text_blocks=[OCRTextBlock(text=full_text, confidence=1.0, line_number=1)],
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


async def process_evidence(file_path: str, file_type: str, evidence_id: str) -> OCRResult:
    """
    Route evidence to the appropriate processor based on file type.
    This is the main entry point for the OCR pipeline.
    Uses asyncio.to_thread to avoid blocking the event loop.
    """
    import asyncio

    def _process_sync():
        try:
            if file_type == "image":
                result = process_image_with_gemini(file_path)
            elif file_type == "pdf":
                result = process_pdf(file_path)
            elif file_type == "csv":
                result = process_csv_file(file_path)
            elif file_type in ("text", "email", "document"):
                result = process_text_file(file_path)
            else:
                result = process_text_file(file_path)

            result.evidence_id = evidence_id
            return result

        except Exception as e:
            print(f"[CrimeLens] OCR Error for {evidence_id}: {traceback.format_exc()}")
            return OCRResult(
                evidence_id=evidence_id,
                full_text=f"[OCR Error] Failed to process file: {str(e)}",
                processing_time_ms=0,
            )

    return await asyncio.to_thread(_process_sync)
