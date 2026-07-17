import React from 'react';

interface CoreDisplayProps {
  currentState: 'idle' | 'listening' | 'thinking' | 'speaking';
  voiceLoopActive: boolean;
}

export const CoreDisplay: React.FC<CoreDisplayProps> = ({ currentState, voiceLoopActive }) => {
  const getGlowStateClass = () => {
    if (!voiceLoopActive && currentState === 'idle') return 'state-idle';
    return `state-${currentState}`;
  };

  const getStatusLabel = () => {
    if (!voiceLoopActive) return 'SYSTEM READY';
    switch (currentState) {
      case 'listening': return 'LISTENING';
      case 'thinking': return 'THINKING';
      case 'speaking': return 'SPEAKING';
      default: return 'ACTIVE STANDBY';
    }
  };

  const getCoreColor = () => {
    if (!voiceLoopActive) return 'var(--color-cyan-pure)';
    switch (currentState) {
      case 'listening': return 'var(--color-success)';
      case 'thinking': return 'var(--color-warning)';
      case 'speaking': return 'var(--color-indigo)';
      default: return 'var(--color-cyan-pure)';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
      
      {/* Decorative Outer HUD Elements */}
      <div className="core-ring core-ring-3"></div>
      <div className="core-ring core-ring-2"></div>
      <div className="core-ring core-ring-1" style={{ borderColor: getCoreColor() }}></div>

      {/* Main Core Orb */}
      <div className={`core-pulse ${currentState}`} style={{ boxShadow: `inset 0 0 40px ${getCoreColor()}` }}>
        <div className={`core-glow ${getGlowStateClass()}`} />
        
        {/* Core Center Label */}
        <div style={{ 
          position: 'relative', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          gap: '4px',
          zIndex: 5 
        }}>
          {/* Brand Identity */}
          <span style={{ 
            fontFamily: 'var(--font-display)', 
            fontSize: '32px', 
            fontWeight: 800, 
            letterSpacing: '0.15em', 
            color: '#ffffff',
            textShadow: `0 0 10px ${getCoreColor()}`,
            transition: 'all 0.3s ease'
          }}>
            FRIDAY
          </span>
          
          {/* Status Subtitle */}
          <span style={{ 
            fontFamily: 'var(--font-mono)', 
            fontSize: '11px', 
            fontWeight: 600, 
            letterSpacing: '0.2em', 
            color: getCoreColor(),
            transition: 'color 0.3s ease'
          }}>
            {getStatusLabel()}
          </span>
        </div>

        {/* Ambient Ring Dots */}
        <div style={{
          position: 'absolute',
          width: '10px',
          height: '10px',
          backgroundColor: getCoreColor(),
          borderRadius: '50%',
          top: '0',
          left: '50%',
          transform: 'translateX(-50%)',
          boxShadow: `0 0 10px ${getCoreColor()}`,
          animation: 'spin-slow 8s linear infinite',
          transformOrigin: '0 130px',
          transition: 'background-color 0.3s ease'
        }}></div>
      </div>

      {/* Futuristic Cockpit Coordinate Labels */}
      <div style={{ 
        position: 'absolute', 
        top: '-100px', 
        fontFamily: 'var(--font-mono)', 
        fontSize: '9px', 
        color: 'var(--text-muted)', 
        letterSpacing: '0.1em',
        display: 'flex',
        gap: '40px'
      }}>
        <span>SYS.LOC: 127.0.0.1</span>
        <span>BRND: FRIDAY UI v1.0</span>
      </div>

      <div style={{ 
        position: 'absolute', 
        bottom: '-100px', 
        fontFamily: 'var(--font-mono)', 
        fontSize: '9px', 
        color: 'var(--text-muted)', 
        letterSpacing: '0.1em',
        display: 'flex',
        gap: '40px'
      }}>
        <span>ENGINE: react-vite-ts</span>
        <span>GATEWAY: active-confirm</span>
      </div>
    </div>
  );
};
