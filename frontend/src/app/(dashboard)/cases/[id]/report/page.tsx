'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, AlertTriangle, ShieldCheck, Cpu } from 'lucide-react';
import { reportsAPI } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { Report } from '@/lib/types';
import jsPDF from 'jspdf';

export default function ReportPage({ params }: { params: { id: string } }) {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadReport();
  }, [params.id]);

  async function loadReport() {
    setLoading(true);
    setError('');
    try {
      const res: any = await reportsAPI.get(params.id);
      if (res.success && res.data) {
        setReport(res.data);
      } else {
        setError('No report generated yet. Click generate below.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while loading report.');
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateReport() {
    setGenerating(true);
    try {
      const res: any = await reportsAPI.generate(params.id);
      if (res.success && res.data) {
        setReport(res.data);
        setError('');
      } else {
        alert(res.message || 'Failed to generate report');
      }
    } catch (err: any) {
      alert(err.message || 'An error occurred during report generation.');
    } finally {
      setGenerating(false);
    }
  }

  const exportPDF = () => {
    if (!report) return;

    const doc = new jsPDF();
    let y = 15;

    // Header
    doc.setFontSize(22);
    doc.setTextColor(6, 8, 15);
    doc.text(report.title || 'Investigation Report', 14, y);
    y += 10;

    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(`Generated: ${formatDate(report.generated_at)} | Case ID: ${report.case_id}`, 14, y);
    y += 15;

    // Sections
    report.sections.forEach((section) => {
      if (y > 270) {
        doc.addPage();
        y = 15;
      }

      doc.setFontSize(14);
      doc.setTextColor(124, 58, 237); // Purple section title
      doc.text(section.title, 14, y);
      y += 8;

      doc.setFontSize(11);
      doc.setTextColor(40, 40, 40);

      // Wrap text
      const lines = doc.splitTextToSize(section.content || 'Data index section.', 180);
      lines.forEach((line: string) => {
        if (y > 275) {
          doc.addPage();
          y = 15;
        }
        doc.text(line, 14, y);
        y += 6;
      });

      y += 8; // Spacer between sections
    });

    doc.save(`CrimeLens_Report_${report.case_id}.pdf`);
  };

  if (loading) {
    return (
      <div className="skeleton" style={{ height: 400 }} />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {report ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {/* Actions Bar */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)' }}>
            <button onClick={handleGenerateReport} className="btn btn-secondary" disabled={generating}>
              {generating ? 'Regenerating...' : 'Regenerate Report'}
            </button>
            <button onClick={exportPDF} className="btn btn-primary">
              <Download size={16} />
              <span>Export PDF</span>
            </button>
          </div>

          {/* Report Preview */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', padding: 'var(--space-8)' }}>
            <div style={{ borderBottom: '1px solid var(--border-default)', paddingBottom: 'var(--space-4)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h1 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 800, color: 'var(--text-primary)' }}>
                  {report.title}
                </h1>
                <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                  GEN-ID: {report._id.toUpperCase()} | Generated: {formatDate(report.generated_at)}
                </span>
              </div>
              <ShieldCheck size={32} style={{ color: 'var(--color-success)' }} />
            </div>

            {report.sections.map((section, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 700, color: 'var(--accent-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {section.title}
                </h3>
                <p style={{ fontSize: 'var(--font-size-base)', color: 'var(--text-primary)', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                  {section.content || 'Structured data index section. Refer to respective dashboard tabs for interactive graphs/timelines.'}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state glass-card" style={{ borderStyle: 'dashed', padding: 'var(--space-12)' }}>
          <FileText size={48} style={{ opacity: 0.3, marginBottom: 'var(--space-4)' }} />
          <h3 className="empty-state-title">No Investigation Report Found</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-6)', maxWidth: '400px', margin: '0 auto var(--space-6)' }}>
            Establish case summaries, timelines, and entity classifications by generating a comprehensive report.
          </p>
          <button onClick={handleGenerateReport} className="btn btn-primary" disabled={generating}>
            {generating ? 'Generating Protocol...' : 'Generate Case Report'}
          </button>
        </div>
      )}
    </div>
  );
}
