'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { UploadCloud, File, Trash2, ShieldAlert, CheckCircle, RefreshCw, Eye, Cpu } from 'lucide-react';
import { evidenceAPI } from '@/lib/api';
import { formatFileSize, formatDate, getStatusClass } from '@/lib/utils';
import type { Evidence } from '@/lib/types';

export default function EvidencePage({ params }: { params: { id: string } }) {
  const [evidenceList, setEvidenceList] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [ocrText, setOcrText] = useState('');
  const [loadingOcr, setLoadingOcr] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadEvidence();
  }, [params.id]);

  async function loadEvidence() {
    setLoading(true);
    try {
      const res: any = await evidenceAPI.list(params.id);
      if (res.success && res.data) {
        setEvidenceList(res.data || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      await uploadFiles(filesArray);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArray = Array.from(e.dataTransfer.files);
      await uploadFiles(filesArray);
    }
  };

  async function uploadFiles(files: File[]) {
    setUploading(true);
    try {
      if (files.length === 1) {
        await evidenceAPI.upload(params.id, files[0]);
      } else {
        await evidenceAPI.uploadMultiple(params.id, files);
      }
      await loadEvidence();
    } catch (err: any) {
      alert(err.message || 'Failed to upload evidence');
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(evidenceId: string) {
    if (confirm('Are you sure you want to delete this evidence? All extracted OCR and AI analysis data will be lost.')) {
      try {
        await evidenceAPI.delete(evidenceId);
        if (selectedEvidence?._id === evidenceId) {
          setSelectedEvidence(null);
          setOcrText('');
        }
        await loadEvidence();
      } catch (err: any) {
        alert(err.message || 'Failed to delete evidence');
      }
    }
  }

  async function handleViewOCR(evidence: Evidence) {
    setSelectedEvidence(evidence);
    setOcrText('');
    setLoadingOcr(true);
    try {
      const res: any = await evidenceAPI.getOCR(evidence._id);
      if (res.success && res.data) {
        setOcrText(res.data.full_text || 'No text extracted from this evidence.');
      } else {
        setOcrText('OCR extraction pending or unavailable.');
      }
    } catch (err: any) {
      setOcrText('Failed to load OCR text.');
    } finally {
      setLoadingOcr(false);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* Upload Zone */}
      <div 
        className={`upload-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={handleBrowseClick}
      >
        <input 
          type="file" 
          multiple 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          style={{ display: 'none' }}
        />
        <UploadCloud size={48} className="upload-zone-icon" />
        <h3 className="upload-zone-title">
          {uploading ? 'Processing & Ingesting Files...' : 'Drag & Drop Evidence'}
        </h3>
        <p className="upload-zone-subtitle">
          Screenshots, WhatsApp/Telegram chat logs, emails, PDFs, or CSV files (Max 50MB)
        </p>
      </div>

      <div className="grid-3" style={{ gap: 'var(--space-6)' }}>
        {/* Evidence List Table */}
        <div className="glass-card" style={{ gridColumn: 'span 2', padding: '0', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: 'var(--space-6)', borderBottom: '1px solid var(--border-default)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700 }}>Evidence Files Ingested</h2>
            <button onClick={loadEvidence} className="btn btn-secondary btn-sm" title="Refresh">
              <RefreshCw size={14} />
            </button>
          </div>

          {loading ? (
            <div className="skeleton" style={{ padding: 'var(--space-6)', height: 200 }} />
          ) : evidenceList.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>File Name</th>
                    <th>Size</th>
                    <th>Uploaded At</th>
                    <th>OCR Status</th>
                    <th>AI Analysis</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {evidenceList.map((e, idx) => (
                    <motion.tr 
                      key={e._id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                    >
                      <td style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                        <File size={16} style={{ color: 'var(--accent-primary)', flexShrink: 0 }} />
                        <span style={{ fontWeight: 600, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {e.original_filename}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-xs)' }}>{formatFileSize(e.file_size)}</td>
                      <td>{formatDate(e.created_at)}</td>
                      <td>
                        <span className={`badge ${getStatusClass(e.ocr_status)}`}>
                          <span className="badge-dot" />
                          {e.ocr_status}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getStatusClass(e.analysis_status)}`}>
                          <span className="badge-dot" />
                          {e.analysis_status}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                          <button onClick={() => handleViewOCR(e)} className="btn btn-secondary btn-sm" title="View Extracted Text">
                            <Eye size={14} />
                          </button>
                          <button onClick={() => handleDelete(e._id)} className="btn btn-danger btn-sm" style={{ padding: 'var(--space-2)' }} title="Delete">
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <File size={40} style={{ opacity: 0.3, marginBottom: 'var(--space-3)' }} />
              <p style={{ color: 'var(--text-muted)' }}>No evidence files in locker. Drag & drop files to begin.</p>
            </div>
          )}
        </div>

        {/* OCR Result Panel */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, marginBottom: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Cpu size={18} style={{ color: 'var(--accent-primary)' }} />
            OCR Text Extracted
          </h3>
          
          {selectedEvidence ? (
            <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: '300px' }}>
              <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--text-muted)', marginBottom: 'var(--space-3)', fontWeight: 600 }}>
                FILE: {selectedEvidence.original_filename}
              </div>
              
              {loadingOcr ? (
                <div className="skeleton" style={{ flex: 1 }} />
              ) : (
                <div style={{
                  flex: 1,
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-default)',
                  borderRadius: 'var(--border-radius-md)',
                  padding: 'var(--space-4)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 'var(--font-size-xs)',
                  color: 'var(--text-primary)',
                  overflowY: 'auto',
                  maxHeight: '400px',
                  whiteSpace: 'pre-wrap',
                }}>
                  {ocrText}
                </div>
              )}
            </div>
          ) : (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)', minHeight: '200px' }}>
              Select an evidence file and click the eye button to view extracted OCR text.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
