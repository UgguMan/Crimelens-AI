'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Clock, ShieldAlert, AlertTriangle, Layers, Tag, User } from 'lucide-react';
import { casesAPI } from '@/lib/api';
import { getRiskColor, getRiskLabel, formatDate } from '@/lib/utils';
import type { Case } from '@/lib/types';

export default function CaseOverviewPage({ params }: { params: { id: string } }) {
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCase() {
      try {
        const res: any = await casesAPI.get(params.id);
        if (res.success && res.data) {
          setCaseData(res.data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadCase();
  }, [params.id]);

  if (loading || !caseData) {
    return (
      <div className="skeleton" style={{ height: 300 }} />
    );
  }

  // Extract analysis results if case has been analyzed
  const aiAnalysis = caseData.ai_analysis;
  const keyFindings = aiAnalysis?.key_findings || [];
  const riskScore = caseData.risk_score || 0;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="grid-3"
      style={{ gap: 'var(--space-6)' }}
    >
      <div style={{ gridColumn: 'span 2', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        {/* Summary Card */}
        <div className="glass-card">
          <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Shield size={20} style={{ color: 'var(--accent-primary)' }} />
            Executive Case Summary
          </h2>
          <p style={{ color: 'var(--text-primary)', lineHeight: '1.6', fontSize: 'var(--font-size-base)', whiteSpace: 'pre-wrap' }}>
            {caseData.description || 'No description provided for this case.'}
          </p>
        </div>

        {/* AI Key Findings if analyzed */}
        {aiAnalysis ? (
          <div className="glass-card">
            <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Layers size={20} style={{ color: 'var(--accent-secondary)' }} />
              AI Key Findings
            </h2>
            {keyFindings.length > 0 ? (
              <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', paddingLeft: 'var(--space-4)', color: 'var(--text-primary)' }}>
                {keyFindings.map((finding: string, idx: number) => (
                  <li key={idx} style={{ lineHeight: '1.5' }}>{finding}</li>
                ))}
              </ul>
            ) : (
              <p style={{ color: 'var(--text-secondary)' }}>
                Case analysis was run, but no key findings were generated.
              </p>
            )}
          </div>
        ) : (
          <div className="glass-card" style={{ borderStyle: 'dashed', textAlign: 'center', padding: 'var(--space-10)' }}>
            <AlertTriangle size={32} style={{ color: 'var(--color-warning)', marginBottom: 'var(--space-3)', opacity: 0.8 }} />
            <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>Case Not Yet Analyzed</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', maxWidth: '400px', margin: '0 auto' }}>
              Upload evidence and click &quot;Run Case AI Analysis&quot; at the top to reconstruct timelines, extract entities, map relationships, and detect suspicious patterns.
            </p>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        {/* Risk & Metadata Card */}
        <div className="glass-card">
          <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: 'var(--space-4)' }}>Case Classification</h3>
          <div className="risk-gauge" style={{ marginBottom: 'var(--space-4)' }}>
            <div className="risk-gauge-circle" style={{ width: '120px', height: '120px' }}>
              <svg viewBox="0 0 120 120" style={{ width: '100%', height: '100%' }}>
                <circle cx="60" cy="60" r="50" fill="none" stroke="var(--bg-hover)" strokeWidth="6" />
                <circle
                  cx="60" cy="60" r="50" fill="none"
                  stroke={getRiskColor(riskScore)}
                  strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray={`${(riskScore / 100) * 314} 314`}
                  transform="rotate(-90 60 60)"
                  style={{ transition: 'stroke-dasharray 1s ease-out' }}
                />
              </svg>
              <div className="risk-gauge-value" style={{ fontSize: 'var(--font-size-xl)', color: getRiskColor(riskScore) }}>
                {riskScore}
              </div>
            </div>
            <div className="risk-gauge-label" style={{ fontSize: 'var(--font-size-xs)' }}>
              Risk Score: <span style={{ color: getRiskColor(riskScore), fontWeight: 700 }}>{getRiskLabel(riskScore)}</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', borderTop: '1px solid var(--border-default)', paddingTop: 'var(--space-4)', fontSize: 'var(--font-size-sm)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Status:</span>
              <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{caseData.status.replace('_', ' ')}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Priority:</span>
              <span style={{ fontWeight: 600, textTransform: 'capitalize', color: getRiskColor(riskScore) }}>{caseData.priority}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Evidence Locker:</span>
              <span style={{ fontWeight: 600 }}>{caseData.evidence_count} file(s)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Created:</span>
              <span style={{ fontWeight: 600 }}>{formatDate(caseData.created_at)}</span>
            </div>
          </div>
        </div>

        {/* Case Tags */}
        <div className="glass-card">
          <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Tag size={16} />
            Case Tags
          </h3>
          {caseData.tags && caseData.tags.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              {caseData.tags.map((tag) => (
                <span key={tag} className="badge badge-open" style={{ fontSize: 'var(--font-size-xs)', textTransform: 'none', letterSpacing: 'normal' }}>
                  {tag}
                </span>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>No tags added to this case.</p>
          )}
        </div>
      </div>
    </motion.div>
  );
}
