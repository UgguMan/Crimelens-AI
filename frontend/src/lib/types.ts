/* ============================================================
   CrimeLens AI — TypeScript Type Definitions
   Shared interfaces matching the backend Pydantic models.
   ============================================================ */

// ── User Types ──────────────────────────────────────────────

export type UserRole = 'admin' | 'investigator' | 'viewer';

export interface User {
  _id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// ── Case Types ──────────────────────────────────────────────

export type CaseStatus = 'open' | 'in_progress' | 'closed' | 'archived';
export type CasePriority = 'low' | 'medium' | 'high' | 'critical';

export interface Case {
  _id: string;
  title: string;
  description: string;
  status: CaseStatus;
  priority: CasePriority;
  assigned_to?: string;
  created_by: string;
  tags: string[];
  evidence_count: number;
  risk_score?: number;
  ai_analysis?: AIAnalysisResult;
  created_at: string;
  updated_at: string;
}

export interface CaseCreate {
  title: string;
  description: string;
  priority: CasePriority;
  tags: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ── Evidence Types ──────────────────────────────────────────

export type FileType = 'image' | 'pdf' | 'text' | 'csv' | 'email' | 'document';
export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Evidence {
  _id: string;
  case_id: string;
  filename: string;
  original_filename: string;
  file_type: FileType;
  mime_type: string;
  file_size: number;
  ocr_status: ProcessingStatus;
  analysis_status: ProcessingStatus;
  uploaded_by: string;
  created_at: string;
}

// ── Analysis Types ──────────────────────────────────────────

export interface TimelineEvent {
  time: string;
  event: string;
  event_type: string;
  source: string;
  severity: string;
}

export interface SuspiciousMessage {
  message: string;
  reason: string;
  category: string;
  severity: string;
  confidence: number;
}

export interface PossibleCrime {
  crime: string;
  description: string;
  evidence: string;
  confidence: number;
  legal_section: string;
}

export interface ExtractedEntities {
  people: string[];
  phone_numbers: string[];
  emails: string[];
  locations: string[];
  organizations: string[];
  bank_accounts: string[];
  vehicle_numbers: string[];
  social_media_ids: string[];
  dates: string[];
  times: string[];
  addresses: string[];
  urls: string[];
}

export interface RelationshipNode {
  id: string;
  label: string;
  node_type: string;
  metadata?: Record<string, unknown>;
}

export interface RelationshipEdge {
  source: string;
  target: string;
  edge_type: string;
  label: string;
  weight: number;
}

export interface AIAnalysisResult {
  case_summary: string;
  timeline: TimelineEvent[];
  entities: ExtractedEntities;
  suspicious_messages: SuspiciousMessage[];
  possible_crimes: PossibleCrime[];
  risk_score: number;
  confidence_score: number;
  recommendations: string[];
  conversation_summary: string;
  key_findings: string[];
  relationship_graph: {
    nodes: RelationshipNode[];
    edges: RelationshipEdge[];
  };
}

// ── Report Types ────────────────────────────────────────────

export interface ReportSection {
  title: string;
  content: string;
  section_type: string;
  data?: unknown;
}

export interface Report {
  _id: string;
  case_id: string;
  title: string;
  sections: ReportSection[];
  case_summary: string;
  risk_score?: number;
  confidence_score?: number;
  evidence_count: number;
  entities_count: number;
  threats_count: number;
  generated_by: string;
  generated_at: string;
}

// ── Search Types ────────────────────────────────────────────

export interface SearchResult {
  type: string;
  text: string;
  context?: string;
  relevance: number;
  evidence_id?: string;
  source?: string;
  entity_type?: string;
  category?: string;
  severity?: string;
  reason?: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total: number;
  suggestions: string[];
}

// ── Analytics Types ─────────────────────────────────────────

export interface AnalyticsOverview {
  total_cases: number;
  total_evidence: number;
  total_threats: number;
  active_cases: number;
  cases_by_status: Record<string, number>;
  cases_by_priority: Record<string, number>;
}

// ── Activity Log Types ──────────────────────────────────────

export interface ActivityLog {
  _id: string;
  user_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown>;
  ip_address: string;
  created_at: string;
}

// ── API Response Wrapper ────────────────────────────────────

export interface APIResponse<T = unknown> {
  success: boolean;
  message?: string;
  data?: T;
}
