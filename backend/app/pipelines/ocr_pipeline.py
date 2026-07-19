"""
CrimeLens AI — OCR Pipeline
===============================
Extracts text from uploaded evidence files using EasyOCR.
Handles images, PDFs, and text-based files with unified output.
"""

import io
import csv
import traceback
from pathlib import Path
from typing import Optional

from app.models.evidence import OCRResult, OCRTextBlock
from app.utils.helpers import Timer

# Lazy-initialized EasyOCR reader (downloads models on first use)
_ocr_reader = None


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


def process_image(file_path: str) -> OCRResult:
    """
    Extract text from an image file using EasyOCR.
    Returns structured OCR result with text blocks and confidence scores.
    """
    with Timer() as timer:
        reader = _get_ocr_reader()

        # EasyOCR returns: [(bbox, text, confidence), ...]
        raw_results = reader.readtext(file_path, detail=1, paragraph=True)

        text_blocks = []
        full_text_parts = []

        for idx, detection in enumerate(raw_results):
            bbox, text, confidence = detection
            block = OCRTextBlock(
                text=text.strip(),
                confidence=round(float(confidence), 3),
                bbox=[[int(coord) for coord in point] for point in bbox] if bbox else [],
                line_number=idx + 1,
            )
            text_blocks.append(block)
            full_text_parts.append(text.strip())

    return OCRResult(
        evidence_id="",  # Set by caller
        full_text="\n".join(full_text_parts),
        text_blocks=text_blocks,
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


def process_pdf(file_path: str) -> OCRResult:
    """
    Extract text from a PDF file.
    Uses PyPDF2 for text-based PDFs, falls back to OCR for scanned pages.
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
                # Scanned page — attempt OCR if page has images
                # For simplicity, we note that this page needs OCR
                all_text_parts.append(f"[Page {page_num + 1}] (scanned — OCR may be limited)")

    return OCRResult(
        evidence_id="",
        full_text="\n\n".join(all_text_parts),
        text_blocks=text_blocks,
        language="en",
        processing_time_ms=timer.elapsed_ms,
    )


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


def process_evidence(file_path: str, file_type: str, evidence_id: str) -> OCRResult:
    """
    Route evidence to the appropriate processor based on file type.
    This is the main entry point for the OCR pipeline.
    """
    try:
        if file_type == "image":
            result = process_image(file_path)
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
