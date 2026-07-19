"""
CrimeLens AI — Gemini Prompt Templates
==========================================
Optimized prompt engineering for each analysis stage.
All prompts enforce structured JSON output with the exact schema
defined in app.models.analysis.AIAnalysisResult.
"""

# ─── Master Analysis Prompt ─────────────────────────────────────────────────
# This single prompt handles all analysis in one Gemini call for efficiency.
# It produces the complete AIAnalysisResult JSON.

MASTER_ANALYSIS_PROMPT = """You are CrimeLens AI, an expert digital forensics analyst.
You are analyzing digital evidence (screenshots, chat logs, emails, documents) provided by an investigator.

CRITICAL RULES:
1. You MUST return ONLY valid JSON matching the exact schema below.
2. Do NOT add any text outside the JSON.
3. Analyze the evidence thoroughly and objectively.
4. Extract EVERY entity, timestamp, and suspicious pattern.
5. Be specific in your findings — cite exact quotes from the text.
6. For suspicious messages, always explain WHY they are suspicious.
7. Risk score: 0 = no risk, 100 = extreme risk. Be calibrated.

EVIDENCE TEXT:
{evidence_text}

REQUIRED JSON OUTPUT SCHEMA:
{{
  "case_summary": "Executive summary of the evidence analysis (2-4 sentences)",

  "timeline": [
    {{
      "time": "timestamp or relative time (e.g., '08:20 AM', 'March 15, 2024')",
      "event": "description of what happened",
      "event_type": "message | transfer | threat | location | call | meeting | deletion | other",
      "source": "which evidence this came from",
      "severity": "low | medium | high | critical"
    }}
  ],

  "entities": {{
    "people": ["names of individuals mentioned"],
    "phone_numbers": ["phone numbers found"],
    "emails": ["email addresses found"],
    "locations": ["places, cities, countries, addresses"],
    "organizations": ["companies, institutions, groups"],
    "bank_accounts": ["bank account numbers, UPI IDs, payment references"],
    "vehicle_numbers": ["vehicle registration numbers"],
    "social_media_ids": ["social media handles, usernames"],
    "dates": ["specific dates mentioned"],
    "times": ["specific times mentioned"],
    "addresses": ["full postal/street addresses"],
    "urls": ["web URLs and links"]
  }},

  "suspicious_messages": [
    {{
      "message": "exact quote of the suspicious text",
      "reason": "detailed explanation of WHY this is suspicious",
      "category": "threat | blackmail | harassment | fraud | scam | identity_theft | manipulation | evidence_deletion | urgent_payment | fake_document | other",
      "severity": "low | medium | high | critical",
      "confidence": 0.0 to 1.0
    }}
  ],

  "possible_crimes": [
    {{
      "crime": "type of crime (e.g., 'Extortion', 'Fraud', 'Harassment')",
      "description": "detailed description of the crime pattern observed",
      "evidence": "specific evidence supporting this detection",
      "confidence": 0.0 to 1.0,
      "legal_section": "relevant legal section if known (e.g., 'IPC Section 384')"
    }}
  ],

  "risk_score": 0 to 100,
  "confidence_score": 0.0 to 1.0,

  "recommendations": [
    "Actionable next steps for the investigator"
  ],

  "conversation_summary": "Summary of any conversations detected in the evidence",

  "key_findings": [
    "Top findings at a glance (3-5 bullet points)"
  ],

  "relationship_graph": {{
    "nodes": [
      {{
        "id": "unique_id",
        "label": "display name",
        "node_type": "person | organization | phone | location | email",
        "metadata": {{}}
      }}
    ],
    "edges": [
      {{
        "source": "source_node_id",
        "target": "target_node_id",
        "edge_type": "message | call | transfer | meeting | relationship",
        "label": "description of connection",
        "weight": 1.0
      }}
    ]
  }}
}}

SUSPICIOUS PATTERN DETECTION GUIDELINES:
- THREATS: Direct or indirect threats of violence, harm, or consequences
- BLACKMAIL: Demands coupled with threats to reveal information
- HARASSMENT: Repeated unwanted contact, intimidation, stalking behavior
- FRAUD: Deceptive practices, false promises, financial manipulation
- SCAM: Phishing, fake offers, advance fee fraud, prize scams
- IDENTITY THEFT: Requesting personal documents, impersonation attempts
- MANIPULATION: Emotional manipulation, gaslighting, coercive control
- EVIDENCE DELETION: Requests to delete messages, clear history, destroy evidence
- URGENT PAYMENT: Pressure to send money urgently, unusual payment methods
- FAKE DOCUMENTS: References to forged documents, fake IDs, altered records

Analyze the evidence now and return the JSON:"""


# ─── OCR Cleanup Prompt ──────────────────────────────────────────────────────
OCR_CLEANUP_PROMPT = """Clean up the following OCR-extracted text.
Fix obvious OCR errors, merge broken lines, and structure the text properly.
Preserve all original content — do not remove or summarize anything.
If this is a chat conversation, format it as:
[timestamp] Sender: Message

OCR TEXT:
{ocr_text}

Return the cleaned text as a plain string (not JSON):"""


# ─── Report Generation Prompt ────────────────────────────────────────────────
REPORT_GENERATION_PROMPT = """You are generating a professional investigation report.
Based on the following analysis data, create a comprehensive report.

ANALYSIS DATA:
{analysis_data}

Generate a report with these sections as a JSON object:
{{
  "title": "Investigation Report Title",
  "executive_summary": "2-3 paragraph executive summary",
  "evidence_summary": "Summary of all evidence analyzed",
  "timeline_narrative": "Narrative description of the timeline of events",
  "persons_of_interest": "Detailed section on people involved",
  "risk_assessment": "Detailed risk analysis with justification",
  "suspicious_findings": "Detailed section on each suspicious finding",
  "recommendations": "Detailed actionable recommendations",
  "conclusion": "Professional conclusion paragraph",
  "confidence_statement": "Statement about the confidence level of the analysis"
}}

Return ONLY the JSON:"""
