'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Database, Users, ArrowRight, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { casesAPI } from '@/lib/api';
import type { CasePriority } from '@/lib/types';

export default function NewCasePage() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<CasePriority>('medium');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim().toLowerCase())) {
        setTags([...tags, tagInput.trim().toLowerCase()]);
      }
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(t => t !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Codename/title is required.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const res: any = await casesAPI.create({
        title: title.trim(),
        description: description.trim(),
        priority,
        tags,
      });

      if (res.success && res.data) {
        router.push(`/cases/${res.data._id}`);
      } else {
        setError(res.message || 'Failed to initialize case.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while creating case.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="page-container"
      style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}
    >
      <div>
        <h1 className="page-title">Initialize Investigation</h1>
        <p className="page-subtitle">Establish a new secure case environment with isolated data silos.</p>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-danger)', background: 'var(--color-danger-bg)', padding: 'var(--space-4)', borderRadius: 'var(--border-radius-md)' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        <div className="grid-2">
          <div className="input-group">
            <label>Operation Codename</label>
            <input 
              type="text" 
              required 
              className="input" 
              placeholder="e.g. Operation Silk Road"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          
          <div className="input-group">
            <label>Case Priority</label>
            <select 
              className="input"
              value={priority}
              onChange={(e) => setPriority(e.target.value as CasePriority)}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>
        
        <div className="input-group">
          <label>Investigation Objectives & Summary</label>
          <textarea 
            required 
            rows={5} 
            className="input" 
            placeholder="Outline primary targets, scope, and objectives..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="input-group">
          <label>Investigation Tags (Press Enter to add)</label>
          <input 
            type="text" 
            className="input" 
            placeholder="e.g. bitcoin, threat-intel, chat-leak"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleAddTag}
          />
          {tags.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
              {tags.map((tag) => (
                <span 
                  key={tag} 
                  className="badge badge-open" 
                  style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', cursor: 'pointer', textTransform: 'none', letterSpacing: 'normal' }}
                  onClick={() => handleRemoveTag(tag)}
                >
                  {tag} &times;
                </span>
              ))}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border-default)', paddingTop: 'var(--space-6)', marginTop: 'var(--space-2)' }}>
          <button type="submit" disabled={loading} className="btn btn-primary">
            <span>{loading ? 'Initializing Protocol...' : 'Launch Investigation'}</span>
            {!loading && <ArrowRight size={16} />}
          </button>
        </div>
      </form>
    </motion.div>
  );
}
