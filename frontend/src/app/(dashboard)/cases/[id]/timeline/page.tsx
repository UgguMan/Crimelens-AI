'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, ShieldAlert, AlertTriangle, AlertCircle, Calendar } from 'lucide-react';
import { evidenceAPI } from '@/lib/api';
import { getRiskColor } from '@/lib/utils';
import type { TimelineEvent } from '@/lib/types';

export default function TimelinePage({ params }: { params: { id: string } }) {
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadTimeline() {
      setLoading(true);
      setError('');
      try {
        const res: any = await evidenceAPI.getCaseAnalysis(params.id);
        if (res.success && res.data) {
          // Sort events chronologically if timestamps are parseable, or rely on AI order
          setTimeline(res.data.timeline || []);
        } else {
          setError('No AI analysis results available for this case. Run Case AI Analysis first.');
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred while loading timeline events.');
      } finally {
        setLoading(false);
      }
    }
    loadTimeline();
  }, [params.id]);

  if (loading) {
    return (
      <div className="skeleton" style={{ height: 400 }} />
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ borderStyle: 'dashed', textAlign: 'center', padding: 'var(--space-10)' }}>
        <AlertTriangle size={32} style={{ color: 'var(--color-warning)', marginBottom: 'var(--space-3)', opacity: 0.8 }} />
        <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>Timeline Pending Analysis</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', maxWidth: '400px', margin: '0 auto' }}>
          {error}
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Calendar size={18} style={{ color: 'var(--accent-primary)' }} />
          Chronological Chronology
        </h2>
      </div>

      {timeline.length > 0 ? (
        <div className="timeline">
          {timeline.map((event, idx) => (
            <motion.div 
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="timeline-item"
            >
              <div className={`timeline-dot ${event.event_type || 'message'}`} style={{ backgroundColor: getRiskColor(event.severity === 'critical' ? 90 : event.severity === 'high' ? 70 : event.severity === 'medium' ? 40 : 10) }} />
              <div className="timeline-time">{event.time}</div>
              <div className="glass-card" style={{ padding: 'var(--space-4) var(--space-5)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-2)' }}>
                  <span style={{ fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--text-accent)', textTransform: 'capitalize' }}>
                    {event.event_type}
                  </span>
                  <span className="badge badge-open" style={{ fontSize: 'var(--font-size-xs)', backgroundColor: 'transparent', border: '1px solid var(--border-default)' }}>
                    Severity: {event.severity}
                  </span>
                </div>
                <div className="timeline-event" style={{ fontSize: 'var(--font-size-base)', fontWeight: 500 }}>
                  {event.event}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="empty-state glass-card">
          <Clock size={40} style={{ opacity: 0.3, marginBottom: 'var(--space-3)' }} />
          <p style={{ color: 'var(--text-muted)' }}>No events could be structured in this timeline.</p>
        </div>
      )}
    </div>
  );
}
