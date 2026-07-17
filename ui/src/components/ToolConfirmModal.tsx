import React from 'react';
import { ShieldAlert, Play, XCircle } from 'lucide-react';
import { ToolCallRequest } from '../api/fridayClient';

interface ToolConfirmModalProps {
  request: ToolCallRequest | null;
  onConfirm: (requestId: string, confirmed: boolean) => void;
}

export const ToolConfirmModal: React.FC<ToolConfirmModalProps> = ({ request, onConfirm }) => {
  if (!request) return null;

  return (
    <div className="dialog-overlay open">
      <div className="dialog-content">
        {/* Modal Header */}
        <div className="dialog-header">
          <div className="dialog-title">
            <ShieldAlert size={20} />
            <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, letterSpacing: '0.05em' }}>
              CONFIRM ACTION REQUIRED
            </span>
          </div>
        </div>

        {/* Modal Body */}
        <div className="dialog-body">
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px', fontSize: '13px' }}>
            Friday Core Engine requires user authorization to execute a tool with external side effects.
          </p>

          {/* Details Container */}
          <div style={{ 
            background: 'rgba(3, 7, 18, 0.5)', 
            border: '1px solid rgba(244, 63, 94, 0.15)', 
            borderRadius: '8px', 
            padding: '16px',
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>TOOL:</span>{' '}
              <span style={{ color: 'var(--color-danger)', fontWeight: 600 }}>{request.toolName}</span>
            </div>
            
            <div>
              <span style={{ color: 'var(--text-muted)' }}>DESC:</span>{' '}
              <span style={{ color: 'var(--text-primary)' }}>{request.description}</span>
            </div>

            <div style={{ marginTop: '8px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>ARGUMENTS:</span>
              <pre style={{ 
                background: 'rgba(0,0,0,0.3)', 
                padding: '10px', 
                borderRadius: '4px', 
                overflowX: 'auto',
                color: 'var(--color-cyan-bright)',
                fontSize: '11px',
                border: '1px solid rgba(255,255,255,0.02)'
              }}>
                {JSON.stringify(request.arguments, null, 2)}
              </pre>
            </div>
          </div>

          <div style={{ 
            marginTop: '16px', 
            fontSize: '11px', 
            color: 'var(--text-muted)', 
            textAlign: 'center', 
            fontStyle: 'italic' 
          }}>
            Rejecting this action will cancel the tool execution and inform the LLM controller.
          </div>
        </div>

        {/* Modal Footer */}
        <div className="dialog-footer">
          <button 
            onClick={() => onConfirm(request.id, false)}
            className="btn-secondary"
            style={{ 
              borderColor: 'rgba(244, 63, 94, 0.4)', 
              color: 'var(--color-danger)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <XCircle size={14} />
            <span>Reject Action</span>
          </button>
          
          <button 
            onClick={() => onConfirm(request.id, true)}
            className="btn-primary"
            style={{ 
              background: 'linear-gradient(135deg, var(--color-danger), #be123c)',
              boxShadow: '0 4px 12px rgba(244, 63, 94, 0.3)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Play size={14} />
            <span>Approve & Execute</span>
          </button>
        </div>
      </div>
    </div>
  );
};
