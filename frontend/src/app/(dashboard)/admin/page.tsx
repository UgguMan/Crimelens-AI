'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, Shield, Server, Activity, Lock, RefreshCw, AlertCircle } from 'lucide-react';
import { adminAPI } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import type { User } from '@/lib/types';

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [systemStats, setSystemStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAdminData();
  }, []);

  async function loadAdminData() {
    setLoading(true);
    setError('');
    try {
      const [usersRes, statsRes]: any[] = await Promise.all([
        adminAPI.listUsers(1),
        adminAPI.getStats(),
      ]);

      if (usersRes.success) {
        setUsers(usersRes.data?.items || []);
      }
      if (statsRes.success) {
        setSystemStats(statsRes.data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load system administration data.');
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleStatus(userId: string, currentStatus: boolean) {
    try {
      const res: any = await adminAPI.updateUser(userId, { is_active: !currentStatus });
      if (res.success) {
        await loadAdminData();
      }
    } catch (err: any) {
      alert(err.message || 'Failed to update user status.');
    }
  }

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title flex" style={{ alignItems: 'center', gap: 'var(--space-2)' }}>
            <Shield size={28} style={{ color: 'var(--accent-primary)' }} />
            System Administration
          </h1>
          <p className="page-subtitle">Manage access controls, system health, and audit logs.</p>
        </div>
        <button onClick={loadAdminData} className="btn btn-secondary" title="Refresh">
          <RefreshCw size={16} />
        </button>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-danger)', background: 'var(--color-danger-bg)', padding: 'var(--space-4)', borderRadius: 'var(--border-radius-md)' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid-3">
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', borderLeft: '4px solid var(--accent-primary)' }}>
          <div style={{ padding: 'var(--space-3)', background: 'rgba(0, 212, 255, 0.12)', borderRadius: 'var(--border-radius-md)' }}>
            <Users size={24} style={{ color: 'var(--accent-primary)' }} />
          </div>
          <div>
            <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>Total Personnel</p>
            <p style={{ fontSize: 'var(--font-size-xl)', fontWeight: 800 }}>
              {loading ? '...' : systemStats?.total_users ?? 0}
            </p>
          </div>
        </div>
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', borderLeft: '4px solid var(--color-success)' }}>
          <div style={{ padding: 'var(--space-3)', background: 'var(--color-success-bg)', borderRadius: 'var(--border-radius-md)' }}>
            <Server size={24} style={{ color: 'var(--color-success)' }} />
          </div>
          <div>
            <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>System Health</p>
            <p style={{ fontSize: 'var(--font-size-xl)', fontWeight: 800, color: 'var(--color-success)' }}>Optimal</p>
          </div>
        </div>
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', borderLeft: '4px solid var(--accent-secondary)' }}>
          <div style={{ padding: 'var(--space-3)', background: 'rgba(124, 58, 237, 0.12)', borderRadius: 'var(--border-radius-md)' }}>
            <Activity size={24} style={{ color: 'var(--accent-secondary)' }} />
          </div>
          <div>
            <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)' }}>Total Cases</p>
            <p style={{ fontSize: 'var(--font-size-xl)', fontWeight: 800 }}>
              {loading ? '...' : systemStats?.total_cases ?? 0}
            </p>
          </div>
        </div>
      </div>

      {/* User Management */}
      <div className="glass-card" style={{ padding: '0', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 'var(--space-6)', borderBottom: '1px solid var(--border-default)' }}>
          <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700 }}>Personnel Access Management</h3>
        </div>

        {loading ? (
          <div className="skeleton" style={{ height: 200 }} />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Operative</th>
                  <th>Email</th>
                  <th>Clearance Role</th>
                  <th>Status</th>
                  <th>Created At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u, idx) => (
                  <motion.tr 
                    key={u._id}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <td style={{ fontWeight: 600 }}>{u.full_name}</td>
                    <td>{u.email}</td>
                    <td>
                      <span className="badge badge-open" style={{ border: '1px solid var(--border-default)', background: 'transparent', textTransform: 'capitalize' }}>
                        {u.role}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${u.is_active ? 'badge-open' : 'badge-closed'}`}>
                        <span className="badge-dot" />
                        {u.is_active ? 'Active' : 'Deactivated'}
                      </span>
                    </td>
                    <td>{formatDate(u.created_at)}</td>
                    <td>
                      <button 
                        onClick={() => handleToggleStatus(u._id, u.is_active)}
                        className={`btn ${u.is_active ? 'btn-danger' : 'btn-primary'} btn-sm`}
                      >
                        {u.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
