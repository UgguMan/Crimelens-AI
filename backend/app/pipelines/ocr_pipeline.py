"""
CrimeLens AI — OCR Pipeline
===============================
Extracts text from uploaded evidence files using EasyOCR.
Handles images, PDFs, and text-based files with unified output.
Runs CPU-bound OCR in a thread pool to avoid blocking the async event loop.
"""

import io
import csv
import asyncio
import traceback
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from app.models.evidence import OCRResult, OCRTextBlock
from app.utils.helpers import Timer

# Lazy-initialized EasyOCR reader (downloads models on first use)
_ocr_reader = None

# Thread pool for CPU-bound OCR work (prevents blocking the async event loop)
_ocr_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ocr")


def _get_ocr_reader():
    """Lazy singleton for EasyOCR reader to avoid loading models on import."""
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        _ocr_reader = easyocr.Reader(
            ["en"],
            gpu=False,  # Set to True if CUDA GPU is available
            verbose=False,
        )
        print("[CrimeLens] EasyOCR reader initialized.")
    return _ocr_reader


def _run_ocr_on_image(file_path: str) -> list[tuple]:
    """
    Run EasyOCR on an image file (blocking call, meant for thread pool).
    Returns raw EasyOCR results.
    """
    reader = _get_ocr_reader()
    # Use detail=1 without paragraph for reliable 3-element tuples
    return reader.readtext(file_path, detail=1, paragraph=False)


def _run_ocr_on_bytes(image_bytes: bytes) -> list[tuple]:
    """
    Run EasyOCR on raw image bytes (for PDF page images).
    """
    reader = _get_ocr_reader()
    return reader.readtext(image_bytes, detail=1, paragraph=False)


def process_image_sync(file_path: str) -> OCRResult:
    """
    Extract text from an image file using EasyOCR.
    Returns structured OCR result with text blocks and confidence scores.
    This is a SYNCHRONOUS function meant to run in a thread pool.
    """
    with Timer() as timer:
        raw_results = _run_ocr_on_image(file_path)

        text_blocks = []
        full_text_parts = []

        for idx, detection in enumerate(raw_results):
            # EasyOCR with detail=1 returns (bbox, text, confidence)
            # Handle both 2-element and 3-element tuples gracefully
            if len(detection) == 3:
                bbox, text, confidence = detection
            elif len(detection) == 2:
                bbox, text = detection
                confidence = 0.5  # Default confidence
            else:
                continue

            text_str = str(text).strip()
            if not text_str:
                continue

            block = OCRTextBlock(
                text=text_str,
                confidence=round(float(confidence), 3),
                bbox=[[int(coord) for coord in point] for point in bbox] if bbox else [],
                line_number=idx + 1,
            )
            text_blocks.append(block)
            full_text_parts.append(text_str)

    return OCRResult(
        evidence_id="",  # Set by caller
        full_text="\n".join(full_text_parts),
        text_blocks=text_blocks,
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


def process_pdf_sync(file_path: str) -> OCRResult:
    """
    Extract text from a PDF file.
    Uses PyPDF2 for text-based PDFs. For scanned pages (no text),
    attempts to render them as images and run OCR.
    This is a SYNCHRONOUS function meant to run in a thread pool.
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
                # Scanned page — try to extract images and OCR them
                ocr_text = _ocr_pdf_page_images(page, page_num)
                if ocr_text:
                    all_text_parts.append(f"[Page {page_num + 1}]\n{ocr_text}")
                    line_counter += 1
                    text_blocks.append(OCRTextBlock(
                        text=ocr_text,
                        confidence=0.7,
                        line_number=line_counter,
                    ))
                else:
                    all_text_parts.append(f"[Page {page_num + 1}] (scanned — no text extracted)")

    return OCRResult(
        evidence_id="",
        full_text="\n\n".join(all_text_parts),
        text_blocks=text_blocks,
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


def _ocr_pdf_page_images(page, page_num: int) -> str:
    """Try to extract images from a PDF page and OCR them."""
    try:
        if not hasattr(page, 'images') or not page.images:
            return ""

        all_text = []
        for img_idx, image in enumerate(page.images):
            try:
                image_bytes = image.data
                if image_bytes and len(image_bytes) > 100:  # Skip tiny images
                    results = _run_ocr_on_bytes(image_bytes)
                    for detection in results:
                        if len(detection) >= 2:
                            text = str(detection[1]).strip()
                            if text:
                                all_text.append(text)
            except Exception:
                continue

        return "\n".join(all_text) if all_text else ""
    except Exception:
        return ""


def process_text_file_sync(file_path: str) -> OCRResult:
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


def process_csv_file_sync(file_path: str) -> OCRResult:
    """Parse CSV files into structured text."""
    with Timer() as timer:
        path = Path(file_path)
        try:
            raw_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_text = path.read_text(encoding="latin-1")

        # Parse CSV and format as readable text
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


def _process_evidence_sync(file_path: str, file_type: str, evidence_id: str) -> OCRResult:
    """
    Synchronous evidence processing (runs in thread pool).
    Routes evidence to the appropriate processor based on file type.
    """
    try:
        if file_type == "image":
            result = process_image_sync(file_path)
        elif file_type == "pdf":
            result = process_pdf_sync(file_path)
        elif file_type == "csv":
            result = process_csv_file_sync(file_path)
        elif file_type in ("text", "email", "document"):
            result = process_text_file_sync(file_path)
        else:
            result = process_text_file_sync(file_path)

        result.evidence_id = evidence_id
        return result

    except Exception as e:
        print(f"[CrimeLens] OCR Error for {evidence_id}: {traceback.format_exc()}")
        return OCRResult(
            evidence_id=evidence_id,
            full_text=f"[OCR Error] Failed to process file: {str(e)}",
            processing_time_ms=0,
        )


async def process_evidence(file_path: str, file_type: str, evidence_id: str) -> OCRResult:
    """
    Async entry point for the OCR pipeline.
    Runs CPU-bound OCR work in a thread pool to avoid blocking the event loop.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _ocr_executor,
        _process_evidence_sync,
        file_path,
        file_type,
        evidence_id,
    )
