'use client';
/* ============================================================
   CrimeLens AI — Dashboard Page
   Cyber command center with stats, recent cases, and activity feed.
   ============================================================ */

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  FolderOpen, FileSearch, AlertTriangle, Shield,
  Plus, Upload, FileText, ArrowRight, Clock,
  TrendingUp, Eye,
} from 'lucide-react';
import { analyticsAPI, casesAPI } from '@/lib/api';
import { formatRelativeTime, getRiskColor, getStatusClass } from '@/lib/utils';
import { useAuth } from '@/lib/auth';
import type { AnalyticsOverview, Case } from '@/lib/types';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [recentCases, setRecentCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [analyticsRes, casesRes]: any[] = await Promise.all([
          analyticsAPI.getOverview(),
          casesAPI.list(1, 5),
        ]);
        setOverview(analyticsRes.data);
        setRecentCases(casesRes.data?.items || []);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const stats = [
    {
      label: 'Total Cases',
      value: overview?.total_cases ?? 0,
      icon: FolderOpen,
      color: '#3b82f6',
      bg: 'rgba(59, 130, 246, 0.12)',
    },
    {
      label: 'Active Investigations',
      value: overview?.active_cases ?? 0,
      icon: Eye,
      color: '#00d4ff',
      bg: 'rgba(0, 212, 255, 0.12)',
    },
    {
      label: 'Evidence Analyzed',
      value: overview?.total_evidence ?? 0,
      icon: FileSearch,
      color: '#7c3aed',
      bg: 'rgba(124, 58, 237, 0.12)',
    },
    {
      label: 'Threats Detected',
      value: overview?.total_threats ?? 0,
      icon: AlertTriangle,
      color: '#ef4444',
      bg: 'rgba(239, 68, 68, 0.12)',
    },
  ];

  return (
    <div className="page-container">
      <motion.div variants={containerVariants} initial="hidden" animate="visible">
        {/* Header */}
        <motion.div variants={itemVariants} className="page-header">
          <div>
            <h1 className="page-title">Command Center</h1>
            <p className="page-subtitle">
              Welcome back, {user?.full_name}. Here&apos;s your investigation overview.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
            <Link href="/cases/new" className="btn btn-primary">
              <Plus size={18} /> New Case
            </Link>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div variants={itemVariants} className="stats-grid" style={{ marginBottom: 'var(--space-8)' }}>
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              className="glass-card stat-card"
              variants={itemVariants}
              whileHover={{ scale: 1.02 }}
            >
              <div className="stat-icon" style={{ background: stat.bg }}>
                <stat.icon size={24} color={stat.color} />
              </div>
              <div className="stat-value" style={{ color: stat.color }}>
                {loading ? (
                  <div className="skeleton" style={{ width: 60, height: 36 }} />
                ) : (
                  <AnimatedCounter value={stat.value} />
                )}
              </div>
              <div className="stat-label">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Content Grid */}
        <div className="grid-2">
          {/* Recent Cases */}
          <motion.div variants={itemVariants} className="glass-card">
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              marginBottom: 'var(--space-6)',
            }}>
              <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700 }}>Recent Cases</h2>
              <Link href="/cases" className="btn btn-ghost btn-sm">
                View All <ArrowRight size={14} />
              </Link>
            </div>

            {loading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 60, marginBottom: 'var(--space-3)' }} />
              ))
            ) : recentCases.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {recentCases.map((c) => (
                  <Link
                    key={c._id}
                    href={`/cases/${c._id}`}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 'var(--space-4)',
                      padding: 'var(--space-3) var(--space-4)',
                      borderRadius: 'var(--border-radius-md)',
                      border: '1px solid var(--border-default)',
                      transition: 'all var(--transition-fast)',
                      textDecoration: 'none', color: 'inherit',
                    }}
                    className="search-result"
                  >
                    <FolderOpen size={18} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontSize: 'var(--font-size-base)', fontWeight: 600,
                        whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                      }}>
                        {c.title}
                      </div>
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                        {c.evidence_count} evidence · {formatRelativeTime(c.created_at)}
                      </div>
                    </div>
                    <span className={`badge ${getStatusClass(c.status)}`}>
                      <span className="badge-dot" />
                      {c.status.replace('_', ' ')}
                    </span>
                    {c.risk_score != null && (
                      <span style={{
                        fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-sm)',
                        fontWeight: 700, color: getRiskColor(c.risk_score),
                      }}>
                        {c.risk_score}
                      </span>
                    )}
                  </Link>
                ))}
              </div>
            ) : (
              <div className="empty-state" style={{ padding: 'var(--space-8)' }}>
                <FolderOpen size={40} style={{ opacity: 0.3, marginBottom: 'var(--space-3)' }} />
                <p style={{ color: 'var(--text-muted)' }}>No cases yet. Create your first case.</p>
                <Link href="/cases/new" className="btn btn-primary btn-sm" style={{ marginTop: 'var(--space-4)' }}>
                  <Plus size={16} /> Create Case
                </Link>
              </div>
            )}
          </motion.div>

          {/* Quick Actions + Threat Overview */}
          <motion.div variants={itemVariants} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
            {/* Quick Actions */}
            <div className="glass-card">
              <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: 'var(--space-5)' }}>
                Quick Actions
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {[
                  { label: 'New Investigation Case', icon: Plus, href: '/cases/new', color: '#00d4ff' },
                  { label: 'Upload Evidence', icon: Upload, href: '/cases', color: '#7c3aed' },
                  { label: 'Generate Report', icon: FileText, href: '/cases', color: '#3b82f6' },
                ].map((action) => (
                  <Link
                    key={action.label}
                    href={action.href}
                    className="search-result"
                    style={{
                      display: 'flex', alignItems: 'center', gap: 'var(--space-3)',
                      padding: 'var(--space-3) var(--space-4)',
                      borderRadius: 'var(--border-radius-md)',
                      border: '1px solid var(--border-default)',
                      textDecoration: 'none', color: 'inherit',
                    }}
                  >
                    <div style={{
                      width: 36, height: 36, borderRadius: 'var(--border-radius-md)',
                      background: `${action.color}15`, display: 'flex',
                      alignItems: 'center', justifyContent: 'center',
                    }}>
                      <action.icon size={18} color={action.color} />
                    </div>
                    <span style={{ fontWeight: 500 }}>{action.label}</span>
                    <ArrowRight size={16} style={{ marginLeft: 'auto', color: 'var(--text-muted)' }} />
                  </Link>
                ))}
              </div>
            </div>

            {/* Threat Level */}
            <div className="glass-card" style={{ flex: 1 }}>
              <h2 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: 'var(--space-5)' }}>
                Threat Overview
              </h2>
              <div className="risk-gauge">
                <div className="risk-gauge-circle">
                  <svg viewBox="0 0 160 160" style={{ width: '100%', height: '100%' }}>
                    {/* Background ring */}
                    <circle cx="80" cy="80" r="70" fill="none" stroke="var(--bg-hover)" strokeWidth="8" />
                    {/* Active ring */}
                    <circle
                      cx="80" cy="80" r="70" fill="none"
                      stroke={getRiskColor(overview?.total_threats ?? 0)}
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${Math.min((overview?.total_threats ?? 0) * 4.4, 440)} 440`}
                      transform="rotate(-90 80 80)"
                      style={{ transition: 'stroke-dasharray 1s ease-out' }}
                    />
                  </svg>
                  <div className="risk-gauge-value" style={{
                    color: getRiskColor(overview?.total_threats ?? 0),
                  }}>
                    {overview?.total_threats ?? 0}
                  </div>
                </div>
                <div className="risk-gauge-label">Threats Detected</div>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}

/** Animated number counter component */
function AnimatedCounter({ value }: { value: number }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (value === 0) { setCount(0); return; }
    const duration = 1000;
    const steps = 30;
    const increment = value / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [value]);

  return <>{count}</>;
}
