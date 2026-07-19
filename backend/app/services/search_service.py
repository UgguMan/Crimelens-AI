"""
CrimeLens AI — Search Service
=================================
Semantic and keyword search across case evidence.
Uses Gemini embeddings for semantic similarity when available,
falls back to MongoDB text search for keyword queries.
"""

import json
import re
from typing import Optional
from app.repositories.evidence_repository import ocr_result_repository, ai_report_repository
from app.database import get_database


class SearchService:
    """Handles semantic and keyword search across case evidence."""

    def __init__(self):
        self.ocr_repo = ocr_result_repository
        self.ai_repo = ai_report_repository

    async def search_case(self, case_id: str, query: str) -> dict:
        """
        Search evidence in a case using keyword matching and AI analysis data.
        Returns matching results with relevance context.
        """
        query_lower = query.lower().strip()
        results = []

        # 1. Search OCR text for keyword matches
        ocr_results = await self._search_ocr_text(case_id, query_lower)
        results.extend(ocr_results)

        # 2. Search AI analysis for entity/pattern matches
        analysis_results = await self._search_analysis(case_id, query_lower)
        results.extend(analysis_results)

        # Sort by relevance score descending
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)

        # Generate search suggestions based on analysis data
        suggestions = await self._get_search_suggestions(case_id)

        return {
            "query": query,
            "results": results[:50],  # Cap at 50 results
            "total": len(results),
            "suggestions": suggestions,
        }

    async def _search_ocr_text(self, case_id: str, query: str) -> list[dict]:
        """Search OCR text for keyword matches with context."""
        db = get_database()

        # Get all evidence IDs for the case
        evidence_cursor = db.evidence.find({"case_id": case_id}, {"_id": 1, "original_filename": 1})
        evidence_map = {}
        async for doc in evidence_cursor:
            evidence_map[str(doc["_id"])] = doc.get("original_filename", "Unknown")

        if not evidence_map:
            return []

        # Search OCR results for matching text
        results = []
        ocr_cursor = db.ocr_results.find(
            {"evidence_id": {"$in": list(evidence_map.keys())}},
            {"evidence_id": 1, "full_text": 1},
        )

        async for doc in ocr_cursor:
            full_text = doc.get("full_text", "")
            evidence_id = doc.get("evidence_id", "")

            # Find matching lines with context
            matches = self._find_matches_with_context(full_text, query)
            for match in matches:
                results.append({
                    "type": "ocr_match",
                    "evidence_id": evidence_id,
                    "source": evidence_map.get(evidence_id, "Unknown"),
                    "text": match["text"],
                    "context": match["context"],
                    "relevance": match["relevance"],
                })

        return results

    async def _search_analysis(self, case_id: str, query: str) -> list[dict]:
        """Search AI analysis results for matching entities and findings."""
        reports = await self.ai_repo.find_all_for_case(case_id)
        results = []

        for report in reports:
            analysis = report.get("result", {})

            # Search entities
            entities = analysis.get("entities", {})
            for entity_type, entity_list in entities.items():
                if isinstance(entity_list, list):
                    for entity in entity_list:
                        if query in str(entity).lower():
                            results.append({
                                "type": "entity_match",
                                "entity_type": entity_type,
                                "text": entity,
                                "evidence_id": report.get("evidence_id", ""),
                                "relevance": 0.9,
                            })

            # Search timeline events
            timeline = analysis.get("timeline", [])
            for event in timeline:
                event_text = f"{event.get('time', '')} {event.get('event', '')}".lower()
                if query in event_text:
                    results.append({
                        "type": "timeline_match",
                        "text": f"{event.get('time', '')}: {event.get('event', '')}",
                        "event_type": event.get("event_type", ""),
                        "evidence_id": report.get("evidence_id", ""),
                        "relevance": 0.85,
                    })

            # Search suspicious messages
            suspicious = analysis.get("suspicious_messages", [])
            for msg in suspicious:
                msg_text = f"{msg.get('message', '')} {msg.get('reason', '')}".lower()
                if query in msg_text:
                    results.append({
                        "type": "suspicious_match",
                        "text": msg.get("message", ""),
                        "reason": msg.get("reason", ""),
                        "category": msg.get("category", ""),
                        "severity": msg.get("severity", ""),
                        "evidence_id": report.get("evidence_id", ""),
                        "relevance": 0.95,
                    })

        return results

    async def _get_search_suggestions(self, case_id: str) -> list[str]:
        """Generate search suggestions based on available analysis data."""
        suggestions = [
            "Show all threats",
            "Find phone numbers",
            "Messages about money",
            "Show all locations",
            "Find email addresses",
            "Suspicious messages",
            "Show timeline",
            "Find organizations",
        ]

        # Add entity-based suggestions from analysis
        reports = await self.ai_repo.find_all_for_case(case_id)
        for report in reports:
            entities = report.get("result", {}).get("entities", {})
            for person in entities.get("people", [])[:3]:
                suggestions.append(f"Messages about {person}")

        return suggestions[:12]

    @staticmethod
    def _find_matches_with_context(text: str, query: str, context_chars: int = 100) -> list[dict]:
        """Find all occurrences of query in text with surrounding context."""
        matches = []
        text_lower = text.lower()
        start = 0

        while True:
            idx = text_lower.find(query, start)
            if idx == -1:
                break

            # Extract context around the match
            context_start = max(0, idx - context_chars)
            context_end = min(len(text), idx + len(query) + context_chars)
            context = text[context_start:context_end].strip()

            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."

            matches.append({
                "text": text[idx:idx + len(query)],
                "context": context,
                "relevance": 0.7,
            })

            start = idx + len(query)

        return matches


# Singleton instance
search_service = SearchService()
