/* ============================================================
   CrimeLens AI — Utility Functions
   ============================================================ */

/**
 * Format file size in bytes to human-readable string.
 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

/**
 * Format ISO date string to readable format.
 */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

/**
 * Format ISO date string to relative time (e.g., "2 hours ago").
 */
export function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(dateStr);
}

/**
 * Get CSS color for risk score.
 */
export function getRiskColor(score: number): string {
  if (score < 20) return 'var(--risk-low)';
  if (score < 50) return 'var(--risk-medium)';
  if (score < 75) return 'var(--risk-high)';
  return 'var(--risk-critical)';
}

/**
 * Get risk level label from score.
 */
export function getRiskLabel(score: number): string {
  if (score < 20) return 'Low';
  if (score < 50) return 'Medium';
  if (score < 75) return 'High';
  return 'Critical';
}

/**
 * Get user initials from full name.
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

/**
 * Truncate text with ellipsis.
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Get icon name for file type.
 */
export function getFileTypeIcon(fileType: string): string {
  const icons: Record<string, string> = {
    image: 'Image',
    pdf: 'FileText',
    text: 'FileType',
    csv: 'Sheet',
    email: 'Mail',
    document: 'File',
  };
  return icons[fileType] || 'File';
}

/**
 * Get status badge CSS class.
 */
export function getStatusClass(status: string): string {
  const classes: Record<string, string> = {
    open: 'badge-open',
    in_progress: 'badge-in-progress',
    closed: 'badge-closed',
    archived: 'badge-closed',
    critical: 'badge-critical',
    high: 'badge-high',
    medium: 'badge-medium',
    low: 'badge-low',
  };
  return classes[status] || 'badge-open';
}

/**
 * Map action string to human-readable label.
 */
export function formatAction(action: string): string {
  const labels: Record<string, string> = {
    'user.registered': 'Registered',
    'user.logged_in': 'Logged in',
    'case.created': 'Created case',
    'case.updated': 'Updated case',
    'case.deleted': 'Deleted case',
    'case.analyzed': 'Analyzed case',
    'evidence.uploaded': 'Uploaded evidence',
    'evidence.deleted': 'Deleted evidence',
    'report.generated': 'Generated report',
    'admin.user_updated': 'Updated user',
  };
  return labels[action] || action;
}
