'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, ShieldAlert, Cpu, Calendar, AlertCircle } from 'lucide-react';
import { searchAPI } from '@/lib/api';
import type { SearchResult } from '@/lib/types';

export default function SearchPage({ params }: { params: { id: string } }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([
    "Show all threats",
    "Find phone numbers",
    "Messages about money",
    "Show all locations",
    "Find email addresses",
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSearch(searchQuery: string) {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res: any = await searchAPI.search(params.id, searchQuery);
      if (res.success && res.data) {
        setResults(res.data.results || []);
        if (res.data.suggestions) {
          setSuggestions(res.data.suggestions);
        }
      } else {
        setError(res.message || 'Search failed');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during search.');
    } finally {
      setLoading(false);
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    handleSearch(suggestion);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Search Input */}
      <div className="glass-card" style={{ display: 'flex', gap: 'var(--space-3)', padding: 'var(--space-4)' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            placeholder="Ask natural language questions: e.g. Who contacted Alex? Find bank accounts..." 
            className="input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
            style={{ paddingLeft: 40 }}
          />
        </div>
        <button onClick={() => handleSearch(query)} className="btn btn-primary" disabled={loading}>
          Search
        </button>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--color-danger)', background: 'var(--color-danger-bg)', padding: 'var(--space-4)', borderRadius: 'var(--border-radius-md)' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
          {suggestions.map((s) => (
            <button 
              key={s} 
              onClick={() => handleSuggestionClick(s)}
              className="badge badge-open" 
              style={{ border: '1px solid var(--border-default)', background: 'transparent', cursor: 'pointer', textTransform: 'none', letterSpacing: 'normal', padding: 'var(--space-2) var(--space-3)' }}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Results */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 100 }} />
          ))
        ) : results.length > 0 ? (
          results.map((r, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="glass-card search-result"
              style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--font-size-xs)', fontWeight: 600, color: 'var(--accent-primary)', textTransform: 'uppercase' }}>
                  {r.type === 'ocr_match' ? <Cpu size={14} /> : r.type === 'timeline_match' ? <Calendar size={14} /> : <ShieldAlert size={14} />}
                  {r.type.replace('_', ' ')}
                </span>
                {r.source && (
                  <span style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)' }}>
                    SOURCE: {r.source}
                  </span>
                )}
              </div>
              <div style={{ fontSize: 'var(--font-size-base)', fontWeight: 600, color: 'var(--text-primary)' }}>
                {r.text}
              </div>
              {r.context && (
                <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', background: 'var(--bg-secondary)', padding: 'var(--space-3)', borderRadius: 'var(--border-radius-sm)', borderLeft: '3px solid var(--accent-primary)', fontFamily: 'var(--font-mono)' }}>
                  {r.context}
                </div>
              )}
              {r.reason && (
                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-warning)' }}>
                  Reason: {r.reason}
                </div>
              )}
            </motion.div>
          ))
        ) : query ? (
          <div className="empty-state glass-card">
            <Search size={40} style={{ opacity: 0.3, marginBottom: 'var(--space-3)' }} />
            <p style={{ color: 'var(--text-muted)' }}>No matches found for &quot;{query}&quot;.</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
