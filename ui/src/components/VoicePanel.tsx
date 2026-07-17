import React, { useEffect, useState } from 'react';
import { Mic, MicOff, ShieldAlert } from 'lucide-react';

interface VoicePanelProps {
  voiceLoopActive: boolean;
  onToggleVoiceLoop: (active: boolean) => void;
  currentState: 'idle' | 'listening' | 'thinking' | 'speaking';
}

export const VoicePanel: React.FC<VoicePanelProps> = ({ 
  voiceLoopActive, 
  onToggleVoiceLoop,
  currentState 
}) => {
  const [waveHeights, setWaveHeights] = useState<number[]>(Array(18).fill(15));

  // Animate mock waveform based on states
  useEffect(() => {
    if (!voiceLoopActive) {
      setWaveHeights(Array(18).fill(15));
      return;
    }

    let intervalId: number;

    const updateWave = () => {
      setWaveHeights(prev => prev.map(() => {
        let min = 10;
        let max = 30;

        if (currentState === 'listening') {
          min = 20;
          max = 75;
        } else if (currentState === 'speaking') {
          min = 35;
          max = 95;
        } else if (currentState === 'thinking') {
          min = 15;
          max = 45;
        } else {
          // idle active
          min = 12;
          max = 25;
        }

        return Math.floor(Math.random() * (max - min + 1)) + min;
      }));
    };

    intervalId = window.setInterval(updateWave, 100);

    return () => {
      clearInterval(intervalId);
    };
  }, [voiceLoopActive, currentState]);

  const getStateText = () => {
    if (!voiceLoopActive) return 'VOICE COMMAND STANDBY';
    switch (currentState) {
      case 'listening': return 'LISTENING FOR SPEECH...';
      case 'thinking': return 'PROCESSING INPUT...';
      case 'speaking': return 'FRIDAY SPEAKING...';
      default: return 'VOICE CONTROL ACTIVE';
    }
  };

  const getStatusColor = () => {
    if (!voiceLoopActive) return 'var(--text-muted)';
    switch (currentState) {
      case 'listening': return 'var(--color-success)';
      case 'thinking': return 'var(--color-warning)';
      case 'speaking': return 'var(--color-indigo)';
      default: return 'var(--color-cyan-pure)';
    }
  };

  return (
    <div className="glass-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {voiceLoopActive ? (
            <Mic size={18} style={{ color: getStatusColor(), transition: 'color 0.3s ease' }} />
          ) : (
            <MicOff size={18} style={{ color: 'var(--text-muted)' }} />
          )}
          <span style={{ fontSize: '13px', fontWeight: 700, letterSpacing: '0.05em', color: 'var(--text-secondary)' }}>
            VOICE CHANNEL
          </span>
        </div>
        
        {/* Toggle Button */}
        <button 
          onClick={() => onToggleVoiceLoop(!voiceLoopActive)}
          className="btn-primary"
          style={{ 
            padding: '6px 12px', 
            fontSize: '11px',
            background: voiceLoopActive 
              ? 'linear-gradient(135deg, var(--color-danger), #b91c1c)' 
              : 'linear-gradient(135deg, var(--color-cyan-pure), var(--color-indigo))',
            boxShadow: voiceLoopActive
              ? '0 4px 12px rgba(244, 63, 94, 0.25)'
              : '0 4px 12px rgba(6, 182, 212, 0.25)'
          }}
        >
          {voiceLoopActive ? 'STOP LOOP' : 'START LOOP'}
        </button>
      </div>

      {/* Voice Waveform Mock Graphic */}
      <div className={`waveform-container ${voiceLoopActive ? 'waveform-active' : ''}`}>
        {waveHeights.map((height, idx) => (
          <div 
            key={idx}
            className="wave-bar"
            style={{ 
              height: `${height}%`,
              backgroundColor: getStatusColor(),
              boxShadow: voiceLoopActive ? `0 0 6px ${getStatusColor()}` : 'none',
              transition: 'height 0.1s ease, background-color 0.3s ease'
            }}
          />
        ))}
      </div>

      {/* Control info / Warning */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{ 
          fontSize: '11px', 
          fontFamily: 'var(--font-mono)', 
          fontWeight: 600, 
          color: getStatusColor(),
          letterSpacing: '0.05em',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span className="dot" style={{ 
            backgroundColor: getStatusColor(), 
            width: '6px', 
            height: '6px', 
            boxShadow: voiceLoopActive ? `0 0 6px ${getStatusColor()}` : 'none' 
          }}></span>
          <span>{getStateText()}</span>
        </div>
        <div style={{ display: 'flex', gap: '8px', fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', background: 'rgba(255, 255, 255, 0.02)', padding: '8px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.03)' }}>
          <ShieldAlert size={14} style={{ color: 'var(--color-warning)', flexShrink: 0 }} />
          <span>Automatic safety guard (confirm gates) remains active for critical scripts.</span>
        </div>
      </div>
    </div>
  );
};
