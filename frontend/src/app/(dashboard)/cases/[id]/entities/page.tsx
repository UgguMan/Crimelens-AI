'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, Phone, Mail, MapPin, Building2, CreditCard, Car, AtSign, Calendar, Clock, AlertTriangle, Link } from 'lucide-react';
import { evidenceAPI } from '@/lib/api';
import type { ExtractedEntities } from '@/lib/types';

export default function EntitiesPage({ params }: { params: { id: string } }) {
  const [entities, setEntities] = useState<ExtractedEntities | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadEntities() {
      setLoading(true);
      setError('');
      try {
        const res: any = await evidenceAPI.getCaseAnalysis(params.id);
        if (res.success && res.data) {
          setEntities(res.data.entities || null);
        } else {
          setError('No AI analysis results available for this case. Run Case AI Analysis first.');
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred while loading entities.');
      } finally {
        setLoading(false);
      }
    }
    loadEntities();
  }, [params.id]);

  if (loading) {
    return (
      <div className="skeleton" style={{ height: 400 }} />
    );
  }

  if (error || !entities) {
    return (
      <div className="glass-card" style={{ borderStyle: 'dashed', textAlign: 'center', padding: 'var(--space-10)' }}>
        <AlertTriangle size={32} style={{ color: 'var(--color-warning)', marginBottom: 'var(--space-3)', opacity: 0.8 }} />
        <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>Entities Pending Analysis</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', maxWidth: '400px', margin: '0 auto' }}>
          {error || 'No entities found.'}
        </p>
      </div>
    );
  }

  const sections = [
    { label: 'People Involved', icon: Users, data: entities.people || [], color: '#3b82f6' },
    { label: 'Phone Numbers', icon: Phone, data: entities.phone_numbers || [], color: '#10b981' },
    { label: 'Emails', icon: Mail, data: entities.emails || [], color: '#00d4ff' },
    { label: 'Locations', icon: MapPin, data: entities.locations || [], color: '#e11d48' },
    { label: 'Organizations', icon: Building2, data: entities.organizations || [], color: '#7c3aed' },
    { label: 'Bank Accounts & UPI', icon: CreditCard, data: entities.bank_accounts || [], color: '#f59e0b' },
    { label: 'Vehicles', icon: Car, data: entities.vehicle_numbers || [], color: '#ec4899' },
    { label: 'Social Handles', icon: AtSign, data: entities.social_media_ids || [], color: '#f43f5e' },
    { label: 'Dates Mentioned', icon: Calendar, data: entities.dates || [], color: '#8b5cf6' },
    { label: 'Times Mentioned', icon: Clock, data: entities.times || [], color: '#14b8a6' },
    { label: 'URLs', icon: Link, data: entities.urls || [], color: '#0ea5e9' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="grid-3" style={{ gap: 'var(--space-6)' }}>
        {sections.map((section, idx) => {
          const Icon = section.icon;
          if (section.data.length === 0) return null;
          return (
            <motion.div
              key={section.label}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="glass-card"
              style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}
            >
              <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <div style={{
                  width: '32px', height: '32px', borderRadius: 'var(--border-radius-md)',
                  background: `${section.color}15`, display: 'flex',
                  alignItems: 'center', justifyContent: 'center', flexShrink: 0
                }}>
                  <Icon size={16} color={section.color} />
                </div>
                {section.label}
                <span className="badge badge-open" style={{ marginLeft: 'auto', fontSize: 'var(--font-size-xs)' }}>{section.data.length}</span>
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', maxHeight: '200px', overflowY: 'auto', paddingRight: 'var(--space-1)' }}>
                {section.data.map((item, itemIdx) => (
                  <div 
                    key={itemIdx} 
                    style={{
                      padding: 'var(--space-2) var(--space-3)',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-default)',
                      borderRadius: 'var(--border-radius-md)',
                      fontSize: 'var(--font-size-sm)',
                      fontFamily: section.icon === Phone || section.icon === CreditCard ? 'var(--font-mono)' : 'inherit',
                      color: 'var(--text-primary)',
                      wordBreak: 'break-all',
                    }}
                  >
                    {item}
                  </div>
                ))}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
