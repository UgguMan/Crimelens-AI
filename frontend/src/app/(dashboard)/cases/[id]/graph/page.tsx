'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Share2, AlertTriangle } from 'lucide-react';
import dynamic from 'next/dynamic';
import { evidenceAPI } from '@/lib/api';

// Dynamic import of react-force-graph-2d to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

export default function GraphPage({ params }: { params: { id: string } }) {
  const [graphData, setGraphData] = useState<{ nodes: any[]; links: any[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadGraph() {
      setLoading(true);
      setError('');
      try {
        const res: any = await evidenceAPI.getCaseAnalysis(params.id);
        if (res.success && res.data && res.data.relationship_graph) {
          const rawGraph = res.data.relationship_graph;
          
          // Map backend nodes/edges to the format react-force-graph expects
          const nodes = (rawGraph.nodes || []).map((node: any) => ({
            id: node.id,
            name: node.label || node.id,
            val: node.node_type === 'person' ? 10 : node.node_type === 'organization' ? 8 : 6,
            color: node.node_type === 'person' ? '#3b82f6' : 
                   node.node_type === 'organization' ? '#7c3aed' : 
                   node.node_type === 'phone' ? '#10b981' : 
                   node.node_type === 'location' ? '#e11d48' : '#00d4ff',
            nodeType: node.node_type,
          }));

          const links = (rawGraph.edges || []).map((edge: any) => ({
            source: edge.source,
            target: edge.target,
            label: edge.label || '',
            edgeType: edge.edge_type,
          }));

          setGraphData({ nodes, links });
        } else {
          setError('No AI analysis results available for this case. Run Case AI Analysis first.');
        }
      } catch (err: any) {
        setError(err.message || 'An error occurred while loading relationship graph.');
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [params.id]);

  if (loading) {
    return (
      <div className="skeleton" style={{ height: 500 }} />
    );
  }

  if (error || !graphData || graphData.nodes.length === 0) {
    return (
      <div className="glass-card" style={{ borderStyle: 'dashed', textAlign: 'center', padding: 'var(--space-10)' }}>
        <AlertTriangle size={32} style={{ color: 'var(--color-warning)', marginBottom: 'var(--space-3)', opacity: 0.8 }} />
        <h3 style={{ fontSize: 'var(--font-size-md)', fontWeight: 600, marginBottom: 'var(--space-2)' }}>Relationship Graph Pending Analysis</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', maxWidth: '400px', margin: '0 auto' }}>
          {error || 'No nodes or edges found.'}
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: 'var(--font-size-md)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Share2 size={18} style={{ color: 'var(--accent-primary)' }} />
          Network Intelligence Link Graph
        </h2>
      </div>

      <div className="glass-card" style={{ padding: '0', overflow: 'hidden', height: '500px', position: 'relative', border: '1px solid var(--border-default)', background: 'rgba(6, 8, 15, 0.9)' }}>
        <ForceGraph2D
          graphData={graphData}
          width={900}
          height={500}
          nodeLabel={(node: any) => `${node.name} (${node.nodeType})`}
          nodeColor={(node: any) => node.color}
          nodeVal={(node: any) => node.val}
          linkLabel={(link: any) => link.label}
          linkColor={() => 'rgba(100, 120, 255, 0.2)'}
          linkWidth={1.5}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
        />
        
        {/* Legend */}
        <div style={{
          position: 'absolute',
          bottom: 'var(--space-4)',
          left: 'var(--space-4)',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-default)',
          borderRadius: 'var(--border-radius-md)',
          padding: 'var(--space-3)',
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-2)',
          fontSize: 'var(--font-size-xs)',
          zIndex: 10,
        }}>
          <div style={{ fontWeight: 600, marginBottom: '2px' }}>Node Categories</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6' }} /> Person
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#7c3aed' }} /> Organization
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} /> Phone
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#e11d48' }} /> Location
          </div>
        </div>
      </div>
    </div>
  );
}
