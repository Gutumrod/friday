import React from 'react';
import { Database, ShieldAlert } from 'lucide-react';
import { MemoryFact } from '../api/fridayClient';

interface MemoryPanelProps {
  facts: MemoryFact[];
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({ facts }) => {
  const getCategoryColor = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'user info': return '#10b981'; // Green
      case 'preferences': return '#06b6d4'; // Cyan
      case 'devices': return '#f59e0b'; // Amber
      default: return '#6366f1'; // Indigo
    }
  };

  return (
    <div className="glass-card" style={{ height: '50%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div className="section-header">
        <div className="section-title">
          <Database size={16} className="rail-icon" />
          <span>Memory Vault</span>
        </div>
        <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
          {facts.length} FACTS
        </span>
      </div>

      <div className="section-content" style={{ display: 'flex', flexDirection: 'column', gap: '12px', position: 'relative' }}>
        {/* Terminal Scanline overlay */}
        <div className="scanline-effect" style={{ animationDuration: '6s' }} />

        {facts.map((fact) => (
          <div 
            key={fact.id}
            style={{ 
              background: 'rgba(3, 7, 18, 0.4)',
              border: '1px solid rgba(255, 255, 255, 0.03)',
              borderRadius: '6px',
              padding: '10px 12px',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              display: 'flex',
              flexDirection: 'column',
              gap: '4px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ 
                color: getCategoryColor(fact.category), 
                fontSize: '9px', 
                fontWeight: 700,
                textTransform: 'uppercase',
                border: `1px solid ${getCategoryColor(fact.category)}40`,
                padding: '1px 6px',
                borderRadius: '3px',
                background: `${getCategoryColor(fact.category)}05`
              }}>
                {fact.category}
              </span>
              <span style={{ color: 'var(--text-muted)', fontSize: '9px' }}>{fact.timestamp.split(' ')[1]}</span>
            </div>
            
            <div style={{ color: 'var(--text-primary)', marginTop: '2px', lineHeight: '1.4' }}>
              {fact.content}
            </div>
          </div>
        ))}

        {facts.length === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '12px', color: 'var(--text-muted)' }}>
            <ShieldAlert size={28} />
            <span style={{ fontSize: '12px' }}>No facts found in local memory vault.</span>
          </div>
        )}
      </div>
    </div>
  );
};
