import React, { useState } from 'react';
import { Send, Terminal, Zap } from 'lucide-react';

interface CommandPanelProps {
  onSendCommand: (command: string) => void;
  isLoading: boolean;
}

export const CommandPanel: React.FC<CommandPanelProps> = ({ onSendCommand, isLoading }) => {
  const [commandText, setCommandText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commandText.trim() || isLoading) return;
    onSendCommand(commandText.trim());
    setCommandText('');
  };

  const handleQuickCommand = (cmd: string) => {
    if (isLoading) return;
    onSendCommand(cmd);
  };

  const quickCommands = [
    { label: "Check Hermes Mailbox", cmd: "ตรวจสอบ Hermes mailbox" },
    { label: "OLED TV Power (Safety Demo)", cmd: "เปิดทีวีและเล่น YouTube" },
    { label: "DSLR DSLR Trigger (Safety Demo)", cmd: "สั่งกล้อง Sony ถ่ายภาพ" },
    { label: "Active Timers", cmd: "ขอดูรายการตั้งเวลาปัจจุบัน" }
  ];

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '8px' }}>
      
      {/* Quick Commands Buttons */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '2px' }}>
        <span style={{ 
          fontFamily: 'var(--font-mono)', 
          fontSize: '9px', 
          color: 'var(--text-muted)', 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '4px',
          marginRight: '4px' 
        }}>
          <Zap size={10} style={{ color: 'var(--color-warning)' }} />
          <span>SHORTCUTS:</span>
        </span>
        {quickCommands.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleQuickCommand(q.cmd)}
            disabled={isLoading}
            style={{
              background: 'rgba(15, 23, 42, 0.4)',
              border: '1px solid var(--border-dim)',
              color: 'var(--text-secondary)',
              fontSize: '11px',
              padding: '4px 10px',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
            onMouseOver={(e) => {
              if (!isLoading) {
                e.currentTarget.style.borderColor = 'var(--color-cyan-pure)';
                e.currentTarget.style.color = '#ffffff';
              }
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-dim)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
          >
            {q.label}
          </button>
        ))}
      </div>

      {/* Main Form Input */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', width: '100%', gap: '10px' }}>
        <div style={{ 
          flex: 1, 
          position: 'relative',
          display: 'flex',
          alignItems: 'center'
        }}>
          <Terminal 
            size={16} 
            style={{ 
              position: 'absolute', 
              left: '14px', 
              color: isLoading ? 'var(--color-warning)' : 'var(--color-cyan-pure)',
              transition: 'color 0.3s ease'
            }} 
          />
          <input
            type="text"
            value={commandText}
            onChange={(e) => setCommandText(e.target.value)}
            disabled={isLoading}
            placeholder={isLoading ? "Friday is thinking..." : "Type text command to Friday UI..."}
            style={{
              width: '100%',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-dim)',
              borderRadius: '8px',
              padding: '12px 16px 12px 42px',
              fontSize: '14px',
              color: '#ffffff',
              outline: 'none',
              transition: 'all 0.2s ease',
              boxShadow: 'inset 0 2px 4px rgba(0, 0, 0, 0.3)'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--color-cyan-pure)';
              e.target.style.boxShadow = '0 0 10px rgba(6, 182, 212, 0.15), inset 0 2px 4px rgba(0, 0, 0, 0.3)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--border-dim)';
              e.target.style.boxShadow = 'inset 0 2px 4px rgba(0, 0, 0, 0.3)';
            }}
          />
          {isLoading && (
            <div style={{
              position: 'absolute',
              right: '16px',
              width: '16px',
              height: '16px',
              border: '2px solid rgba(6, 182, 212, 0.1)',
              borderTopColor: 'var(--color-cyan-pure)',
              borderRadius: '50%',
              animation: 'spin-slow 1s linear infinite'
            }} />
          )}
        </div>

        <button
          type="submit"
          disabled={!commandText.trim() || isLoading}
          className="btn-primary"
          style={{
            padding: '0 20px',
            borderRadius: '8px',
            opacity: (!commandText.trim() || isLoading) ? 0.5 : 1,
            cursor: (!commandText.trim() || isLoading) ? 'not-allowed' : 'pointer',
            height: '100%'
          }}
        >
          <Send size={16} />
          <span>Execute</span>
        </button>
      </form>
    </div>
  );
};
