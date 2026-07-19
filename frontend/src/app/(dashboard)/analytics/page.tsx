'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart2, PieChart, Activity, RefreshCw } from 'lucide-react';
import { analyticsAPI } from '@/lib/api';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [crimeTypes, setCrimeTypes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    setLoading(true);
    try {
      const [overRes, crimesRes]: any[] = await Promise.all([
        analyticsAPI.getOverview(),
        analyticsAPI.getCrimeTypes(),
      ]);

      if (overRes.success) setOverview(overRes.data);
      if (crimesRes.success) setCrimeTypes(crimesRes.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // Calculate SVG Pie/Donut Chart parameters
  const totalCases = overview?.total_cases || 0;
  const statuses = overview?.cases_by_status || {};
  const statusLabels = Object.keys(statuses);
  const statusValues = Object.values(statuses) as number[];
  const statusColors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

  let cumulativeOffset = 0;
  const donutCircles = statusValues.map((val, idx) => {
    const percentage = totalCases > 0 ? (val / totalCases) * 100 : 0;
    const strokeDash = `${percentage} ${100 - percentage}`;
    const offset = 100 - cumulativeOffset;
    cumulativeOffset += percentage;

    return {
      dashArray: `${(percentage / 100) * 251.2} 251.2`,
      offset: -((100 - offset) / 100) * 251.2,
      color: statusColors[idx % statusColors.length],
      label: statusLabels[idx],
      value: val,
    };
  });

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title flex" style={{ alignItems: 'center', gap: 'var(--space-2)' }}>
            <BarChart2 size={28} style={{ color: 'var(--accent-primary)' }} />
            Global Intelligence Analytics
          </h1>
          <p className="page-subtitle">Macro-level insights across all active and archived cases.</p>
        </div>
        <button onClick={loadAnalytics} className="btn btn-secondary" title="Refresh">
          <RefreshCw size={16} />
        </button>
      </div>

      {loading ? (
        <div className="skeleton" style={{ height: 400 }} />
      ) : (
        <div className="grid-2">
          {/* Bar Chart */}
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="glass-card">
            <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Activity size={18} style={{ color: 'var(--accent-primary)' }} />
              Threats & Crime Vector Profile
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', minHeight: '260px', justifyContent: 'center' }}>
              {crimeTypes.length > 0 ? (
                crimeTypes.map((c, idx) => {
                  const maxCount = Math.max(...crimeTypes.map((item) => item.count));
                  const percentage = maxCount > 0 ? (c.count / maxCount) * 100 : 0;
                  return (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                      <div style={{ width: '120px', fontSize: 'var(--font-size-sm)', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'capitalize', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {c.crime}
                      </div>
                      <div style={{ flex: 1, background: 'var(--bg-secondary)', height: '12px', borderRadius: 'var(--border-radius-sm)', overflow: 'hidden' }}>
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ duration: 0.8 }}
                          style={{
                            height: '100%',
                            background: 'var(--accent-gradient)',
                            boxShadow: 'var(--shadow-glow)',
                          }}
                        />
                      </div>
                      <div style={{ width: '30px', textAlign: 'right', fontSize: 'var(--font-size-sm)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                        {c.count}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                  No crime vector data profiled yet. Run Case AI Analysis on evidence.
                </div>
              )}
            </div>
          </motion.div>

          {/* Donut Chart */}
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="glass-card">
            <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <PieChart size={18} style={{ color: 'var(--accent-secondary)' }} />
              Case Status Distribution
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '260px' }}>
              {totalCases > 0 ? (
                <>
                  <div style={{ width: '180px', height: '180px', position: 'relative', marginBottom: 'var(--space-4)' }}>
                    <svg viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)', width: '100%', height: '100%' }}>
                      <circle cx="50" cy="50" r="40" fill="transparent" stroke="var(--bg-secondary)" strokeWidth="12" />
                      {donutCircles.map((circle, idx) => (
                        <circle
                          key={idx}
                          cx="50"
                          cy="50"
                          r="40"
                          fill="transparent"
                          stroke={circle.color}
                          strokeWidth="12"
                          strokeDasharray={circle.dashArray}
                          strokeDashoffset={circle.offset}
                          strokeLinecap="round"
                        />
                      ))}
                    </svg>
                    <div style={{
                      position: 'absolute',
                      top: '50%', left: '50%',
                      transform: 'translate(-50%, -50%)',
                      textAlign: 'center',
                    }}>
                      <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 800 }}>{totalCases}</div>
                      <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Cases</div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                    {donutCircles.map((circle, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--font-size-sm)' }}>
                        <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: circle.color }} />
                        <span style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{circle.label.replace('_', ' ')}:</span>
                        <span style={{ fontWeight: 700 }}>{circle.value}</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                  No case data populated yet.
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
