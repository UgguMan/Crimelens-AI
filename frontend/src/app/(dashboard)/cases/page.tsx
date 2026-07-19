'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Plus, Folder, Clock, ShieldAlert, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { casesAPI } from '@/lib/api';
import { formatDate, getStatusClass, getRiskColor } from '@/lib/utils';
import type { Case } from '@/lib/types';

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  useEffect(() => {
    fetchCases();
  }, [statusFilter, priorityFilter]);

  async function fetchCases() {
    setLoading(true);
    setError('');
    try {
      const res: any = await casesAPI.list(1, 100, statusFilter || undefined, priorityFilter || undefined);
      if (res.success && res.data) {
        setCases(res.data.items || []);
      } else {
        setError(res.message || 'Failed to load cases');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while loading cases.');
    } finally {
      setLoading(false);
    }
  }

  // Filter cases locally by search query
  const filteredCases = cases.filter(c => 
    c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Active Investigations</h1>
          <p className="page-subtitle">Manage, analyze, and monitor digital forensic cases</p>
        </div>
        <Link href="/cases/new" className="btn btn-primary">
          <Plus size={18} />
          <span>New Case</span>
        </Link>
      </div>

      {/* Filters Bar */}
      <div className="glass-card" style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center', flexWrap: 'wrap', padding: 'var(--space-4)' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '250px' }}>
          <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            placeholder="Search cases by title or description..." 
            className="input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: 40 }}
          />
        </div>

        <select 
          className="input" 
          style={{ width: '160px' }}
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="closed">Closed</option>
          <option value="archived">Archived</option>
        </select>

        <select 
          className="input" 
          style={{ width: '160px' }}
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
        >
          <option value="">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-danger)', background: 'var(--color-danger-bg)', padding: 'var(--space-4)', borderRadius: 'var(--border-radius-md)' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="grid-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 180 }} />
          ))}
        </div>
      ) : filteredCases.length > 0 ? (
        <div className="grid-3">
          {filteredCases.map((c, i) => (
            <motion.div
              key={c._id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="glass-card"
              whileHover={{ y: -4, borderColor: 'var(--accent-primary)' }}
              style={{ padding: '0', display: 'flex', flexDirection: 'column', height: '100%' }}
            >
              <Link href={`/cases/${c._id}`} style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', flex: 1, color: 'inherit', textDecoration: 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-4)' }}>
                  <div style={{ padding: 'var(--space-2)', background: 'rgba(0, 212, 255, 0.08)', borderRadius: 'var(--border-radius-md)', display: 'flex' }}>
                    <Folder size={24} style={{ color: 'var(--accent-primary)' }} />
                  </div>
                  <span className={`badge ${getStatusClass(c.status)}`}>
                    <span className="badge-dot" />
                    {c.status.replace('_', ' ')}
                  </span>
                </div>
                <h3 style={{ fontSize: 'var(--font-size-lg)', fontWeight: 700, marginBottom: 'var(--space-2)', color: 'var(--text-primary)' }}>{c.title}</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', marginBottom: 'var(--space-4)', flex: 1, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                  {c.description || 'No description provided.'}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-default)', paddingTop: 'var(--space-4)', fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                    <ShieldAlert size={14} style={{ color: getRiskColor(c.risk_score || 0) }} />
                    Priority: <span style={{ fontWeight: 600, color: 'var(--text-primary)', textTransform: 'capitalize' }}>{c.priority}</span>
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                    <Clock size={14} />
                    {formatDate(c.created_at)}
                  </span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="empty-state glass-card">
          <Folder size={48} style={{ opacity: 0.3, marginBottom: 'var(--space-4)' }} />
          <h3 className="empty-state-title">No Cases Found</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-6)' }}>
            Get started by creating a new investigation case.
          </p>
          <Link href="/cases/new" className="btn btn-primary">
            <Plus size={16} /> Create Case
          </Link>
        </div>
      )}
    </div>
  );
}

