'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Database, Key, Shield, RefreshCw } from 'lucide-react';
import { analyticsAPI } from '@/lib/api';
import { formatRelativeTime, formatAction } from '@/lib/utils';
import type { ActivityLog } from '@/lib/types';

export default function ActivityPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  async function loadLogs() {
    setLoading(true);
    try {
      const res: any = await analyticsAPI.getRecentActivity();
      if (res.success && res.data) {
        setLogs(res.data || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title flex" style={{ alignItems: 'center', gap: 'var(--space-2)' }}>
            <Terminal size={28} style={{ color: 'var(--accent-primary)' }} />
            Global Audit Log
          </h1>
          <p className="page-subtitle">Immutable record of all system events and user actions.</p>
        </div>
        <button onClick={loadLogs} className="btn btn-secondary" title="Refresh">
          <RefreshCw size={16} />
        </button>
      </div>

      <div className="glass-card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ padding: 'var(--space-4) var(--space-6)', borderBottom: '1px solid var(--border-default)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(6, 8, 15, 0.4)' }}>
          <div style={{ display: 'flex', gap: 'var(--space-4)', fontSize: 'var(--font-size-xs)', fontFamily: 'var(--font-mono)' }}>
            <span style={{ color: 'var(--accent-primary)' }}>STATUS: RECORDING</span>
            <span style={{ color: 'var(--text-muted)' }}>MODE: STRICT VERIFICATION</span>
          </div>
        </div>
        
        {loading ? (
          <div className="skeleton" style={{ height: 200 }} />
        ) : logs.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {logs.map((log, i) => (
              <motion.div
                key={log._id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                style={{
                  padding: 'var(--space-4) var(--space-6)',
                  borderBottom: '1px solid var(--border-default)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-6)',
                  transition: 'background var(--transition-fast)',
                }}
                className="search-result"
              >
                <div style={{ width: '120px', flexShrink: 0 }}>
                  <span style={{ fontSize: 'var(--font-size-xs)', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    {formatRelativeTime(log.created_at)}
                  </span>
                </div>
                <div style={{
                  padding: 'var(--space-2)',
                  borderRadius: 'var(--border-radius-sm)',
                  background: 'rgba(0, 212, 255, 0.08)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--accent-primary)',
                }}>
                  {log.action.includes('user') ? <Key size={16} /> : log.action.includes('case') ? <Shield size={16} /> : <Database size={16} />}
                </div>
                <div style={{ width: '160px', flexShrink: 0 }}>
                  <span style={{ fontSize: 'var(--font-size-sm)', fontWeight: 600 }}>
                    User: {log.user_id ? 'Operative' : 'System'}
                  </span>
                </div>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                    {formatAction(log.action)} {log.resource_type ? `(${log.resource_type}: ${log.resource_id.slice(-6)})` : ''}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="empty-state" style={{ padding: 'var(--space-12)' }}>
            <Terminal size={40} style={{ opacity: 0.3, marginBottom: 'var(--space-3)' }} />
            <p style={{ color: 'var(--text-muted)' }}>No audit events logged yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
