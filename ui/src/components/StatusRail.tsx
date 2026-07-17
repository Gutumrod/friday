import React from 'react';
import { 
  Cpu, 
  Layers, 
  Mic, 
  Bot, 
  Volume2, 
  Mail, 
  Wifi, 
  Activity 
} from 'lucide-react';
import { SystemStatus } from '../api/fridayClient';

interface StatusRailProps {
  status: SystemStatus;
}

export const StatusRail: React.FC<StatusRailProps> = ({ status }) => {
  return (
    <div className="glass-card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="section-header">
        <div className="section-title">
          <Activity size={16} className="rail-icon" />
          <span>System Status</span>
        </div>
        <div className="indicator">
          <span className={`dot ${status.online ? 'active' : 'error'}`}></span>
          <span>{status.online ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </div>

      <div className="section-content" style={{ display: 'flex', flexDirection: 'column', gap: '4px', padding: 0 }}>
        {/* Core Model */}
        <div className="rail-item">
          <div className="rail-label-container">
            <Bot size={16} className="rail-icon" />
            <span className="rail-name">Model</span>
          </div>
          <span className="rail-value" title={status.model}>
            {status.model.length > 20 ? status.model.substring(0, 18) + '..' : status.model}
          </span>
        </div>

        {/* Microphone Indicator */}
        <div className="rail-item">
          <div className="rail-label-container">
            <Mic size={16} className="rail-icon" />
            <span className="rail-name">Mic Hardware</span>
          </div>
          <div className="indicator">
            <span className={`dot ${status.micConnected ? 'active' : 'error'}`}></span>
            <span className="rail-value">{status.micConnected ? 'CONNECTED' : 'DISCONNECTED'}</span>
          </div>
        </div>

        {/* Speech to Text Engine */}
        <div className="rail-item">
          <div className="rail-label-container">
            <Layers size={16} className="rail-icon" />
            <span className="rail-name">STT Engine</span>
          </div>
          <span className="rail-value">{status.sttEngine}</span>
        </div>

        {/* Text to Speech Engine */}
        <div className="rail-item">
          <div className="rail-label-container">
            <Volume2 size={16} className="rail-icon" />
            <span className="rail-name">TTS Engine</span>
          </div>
          <span className="rail-value">{status.ttsEngine}</span>
        </div>

        {/* Hermes Connection */}
        <div className="rail-item">
          <div className="rail-label-container">
            <Mail size={16} className="rail-icon" />
            <span className="rail-name">Hermes Mailbox</span>
          </div>
          <div className="indicator">
            <span className={`dot ${status.hermesConnected ? 'active' : 'inactive'}`}></span>
            <span className="rail-value">{status.hermesConnected ? 'MONITORED' : 'OFFLINE'}</span>
          </div>
        </div>

        {/* Network Ping */}
        <div className="rail-item">
          <div className="rail-label-container">
            <Wifi size={16} className="rail-icon" />
            <span className="rail-name">Response Latency</span>
          </div>
          <span className="rail-value">{status.networkLatency} ms</span>
        </div>

        {/* Hardware Resource Usage */}
        <div style={{ padding: '20px', marginTop: 'auto', borderTop: '1px solid var(--border-dim)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* CPU Bar */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontFamily: 'var(--font-mono)', marginBottom: '6px', color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Cpu size={12} />
                <span>FRIDAY CPU</span>
              </div>
              <span>{status.cpuUsage}%</span>
            </div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${status.cpuUsage}%`, background: 'var(--color-cyan-pure)', boxShadow: '0 0 8px var(--color-cyan-pure)', transition: 'width 0.5s ease' }}></div>
            </div>
          </div>

          {/* Memory Bar */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontFamily: 'var(--font-mono)', marginBottom: '6px', color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Layers size={12} />
                <span>SYS MEMORY</span>
              </div>
              <span>{status.memoryUsage}%</span>
            </div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${status.memoryUsage}%`, background: 'var(--color-indigo)', boxShadow: '0 0 8px var(--color-indigo)', transition: 'width 0.5s ease' }}></div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
