import React, { useEffect, useRef } from 'react';
import { Terminal, RefreshCw } from 'lucide-react';
import { ActivityLogItem } from '../api/fridayClient';

interface ActivityLogProps {
  logs: ActivityLogItem[];
  onClearLogs?: () => void;
}

export const ActivityLog: React.FC<ActivityLogProps> = ({ logs, onClearLogs }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom on new logs
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="glass-card" style={{ height: '50%', display: 'flex', flexDirection: 'column', overflow: 'hidden', borderTop: 'none', borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}>
      <div className="section-header">
        <div className="section-title">
          <Terminal size={16} className="rail-icon" />
          <span>Activity Stream</span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {onClearLogs && (
            <button 
              onClick={onClearLogs}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                padding: '2px'
              }}
              title="Clear logs"
            >
              <RefreshCw size={12} />
            </button>
          )}
          <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
            LIVE FEED
          </span>
        </div>
      </div>

      <div 
        ref={containerRef}
        className="section-content" 
        style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '2px', 
          overflowY: 'auto',
          padding: '16px 20px',
          scrollBehavior: 'smooth'
        }}
      >
        {logs.map((log) => (
          <div key={log.id} className={`log-item ${log.type}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="log-time">{log.timestamp}</span>
              <span style={{ 
                fontFamily: 'var(--font-mono)', 
                fontSize: '8px', 
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                background: 'rgba(255,255,255,0.02)',
                padding: '1px 4px',
                borderRadius: '2px'
              }}>
                {log.type}
              </span>
            </div>
            <div className="log-desc">{log.message}</div>
            {log.meta && (
              <div className="log-meta">
                {log.meta}
              </div>
            )}
          </div>
        ))}

        {logs.length === 0 && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '12px' }}>
            Awaiting system events...
          </div>
        )}
      </div>
    </div>
  );
};
