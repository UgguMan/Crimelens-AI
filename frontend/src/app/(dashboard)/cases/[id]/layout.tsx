'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, FileText, Activity, Users, Share2, Search, Download, AlertCircle, Play } from 'lucide-react';
import { casesAPI, evidenceAPI } from '@/lib/api';
import { getStatusClass, getRiskColor } from '@/lib/utils';
import type { Case } from '@/lib/types';

export default function CaseDetailLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { id: string };
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchCaseDetails();
  }, [params.id]);

  async function fetchCaseDetails() {
    setLoading(true);
    setError('');
    try {
      const res: any = await casesAPI.get(params.id);
      if (res.success && res.data) {
        setCaseData(res.data);
      } else {
        setError(res.message || 'Failed to load case details');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while loading case details.');
    } finally {
      setLoading(false);
    }
  }

  async function handleRunAnalysis() {
    setAnalyzing(true);
    try {
      const res: any = await evidenceAPI.analyzeCase(params.id);
      if (res.success) {
        // Refresh details
        await fetchCaseDetails();
        // Redirect to timeline or refresh current page
        router.refresh();
      } else {
        alert(res.message || 'Failed to run analysis');
      }
    } catch (err: any) {
      alert(err.message || 'An error occurred during analysis.');
    } finally {
      setAnalyzing(false);
    }
  }

  const tabs = [
    { name: 'Overview', href: `/cases/${params.id}`, icon: Shield },
    { name: 'Evidence Locker', href: `/cases/${params.id}/evidence`, icon: FileText },
    { name: 'Timeline', href: `/cases/${params.id}/timeline`, icon: Activity },
    { name: 'Entity Locker', href: `/cases/${params.id}/entities`, icon: Users },
    { name: 'Relationship Graph', href: `/cases/${params.id}/graph`, icon: Share2 },
    { name: 'Semantic Search', href: `/cases/${params.id}/search`, icon: Search },
    { name: 'Investigation Report', href: `/cases/${params.id}/report`, icon: Download },
  ];

  if (loading) {
    return (
      <div className="page-container">
        <div className="skeleton" style={{ height: 80, marginBottom: 'var(--space-6)' }} />
        <div className="skeleton" style={{ height: 48, marginBottom: 'var(--space-6)' }} />
        <div className="skeleton" style={{ height: 400 }} />
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="page-container">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-danger)', background: 'var(--color-danger-bg)', padding: 'var(--space-4)', borderRadius: 'var(--border-radius-md)' }}>
          <AlertCircle size={18} />
          <span>{error || 'Case not found'}</span>
        </div>
        <Link href="/cases" className="btn btn-secondary" style={{ marginTop: 'var(--space-4)' }}>
          Back to Cases
        </Link>
      </div>
    );
  }

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
            <span className="badge" style={{ background: 'rgba(239, 68, 68, 0.12)', color: 'var(--color-danger)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>TS//SCI</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>CASE-{caseData._id.toUpperCase()}</span>
          </div>
          <h1 className="page-title">{caseData.title}</h1>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button 
            onClick={handleRunAnalysis} 
            className="btn btn-primary"
            disabled={analyzing || caseData.evidence_count === 0}
          >
            <Play size={16} fill="currentColor" />
            <span>{analyzing ? 'Analyzing Case...' : 'Run Case AI Analysis'}</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-default)', overflowX: 'auto', gap: 'var(--space-2)' }}>
        {tabs.map((tab) => {
          const isActive = pathname === tab.href;
          const Icon = tab.icon;
          return (
            <Link 
              key={tab.name}
              href={tab.href}
              className={`btn btn-ghost`}
              style={{
                borderRadius: '0',
                borderBottom: isActive ? '2px solid var(--accent-primary)' : '2px solid transparent',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                padding: 'var(--space-3) var(--space-4)',
                fontWeight: isActive ? 600 : 500,
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-2)',
              }}
            >
              <Icon size={16} />
              <span>{tab.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Page Content */}
      <div style={{ marginTop: 'var(--space-2)' }}>
        {children}
      </div>
    </div>
  );
}
