import React, { useEffect, useState } from 'react';
import { 
  fridayClient, 
  SystemStatus, 
  MemoryFact, 
  ActivityLogItem, 
  ToolCallRequest 
} from './api/fridayClient';

import { StatusRail } from './components/StatusRail';
import { VoicePanel } from './components/VoicePanel';
import { CoreDisplay } from './components/CoreDisplay';
import { MemoryPanel } from './components/MemoryPanel';
import { ActivityLog } from './components/ActivityLog';
import { CommandPanel } from './components/CommandPanel';
import { ToolConfirmModal } from './components/ToolConfirmModal';
import { Shield } from 'lucide-react';

const App: React.FC = () => {
  // State variables
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    online: false,
    model: "Loading...",
    micConnected: false,
    sttEngine: "Loading...",
    ttsEngine: "Loading...",
    hermesConnected: false,
    networkLatency: 0,
    voiceLoopActive: false,
    cpuUsage: 0,
    memoryUsage: 0,
  });

  const [memoryFacts, setMemoryFacts] = useState<MemoryFact[]>([]);
  const [activityLogs, setActivityLogs] = useState<ActivityLogItem[]>([]);
  const [currentState, setCurrentState] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');
  const [activeConfirmRequest, setActiveConfirmRequest] = useState<ToolCallRequest | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [isSendingCommand, setIsSendingCommand] = useState(false);

  // Initialize and load data
  useEffect(() => {
    let wsInstance: { close: () => void } | null = null;

    const loadInitialData = async () => {
      try {
        const [status, facts, logs] = await Promise.all([
          fridayClient.getStatus(),
          fridayClient.getMemoryFacts(),
          fridayClient.getActivityLogs()
        ]);
        setSystemStatus(status);
        setMemoryFacts(facts);
        setActivityLogs(logs);
      } catch (err) {
        console.error("Failed to load initial data", err);
      }
    };

    loadInitialData();

    // Setup Event Listeners
    const handleEvent = (type: string, data: any) => {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      const logId = `log-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
      const confirmationId = data.confirmation_id || data.id;
      const toolName = data.tool_name || data.toolName;
      const toolArgs = data.args || data.arguments || {};
      const toolQuestion = data.question || data.description || `Confirm ${toolName}`;

      switch (type) {
        case 'info':
          setActivityLogs(prev => [...prev, { id: logId, type: 'info', message: String(data), timestamp: timeStr }]);
          break;
        case 'listening_started':
          setCurrentState('listening');
          setSystemStatus(prev => ({ ...prev, voiceLoopActive: true }));
          setActivityLogs(prev => [...prev, { id: logId, type: 'listening', message: "Voice input active. Listening...", timestamp: timeStr }]);
          break;
        case 'stt_result':
          setCurrentState('thinking');
          setActivityLogs(prev => [...prev, { id: logId, type: 'stt', message: `Speech detected: "${data.text}"`, timestamp: timeStr }]);
          break;
        case 'thinking_started':
          setCurrentState('thinking');
          setActivityLogs(prev => [...prev, { id: logId, type: 'thinking', message: "Friday core is thinking...", timestamp: timeStr }]);
          break;
        case 'llm_response':
          setCurrentState('speaking');
          setActivityLogs(prev => [...prev, { id: logId, type: 'llm', message: data.text || data.content || '', timestamp: timeStr }]);
          break;
        case 'tool_requested':
          setActivityLogs(prev => [...prev, {
            id: logId,
            type: 'tool',
            message: "Friday requested tool execution.",
            timestamp: timeStr,
            meta: JSON.stringify(data.tool_calls || data.toolCalls || [])
          }]);
          break;
        case 'tts_started':
          setCurrentState('speaking');
          setActivityLogs(prev => [...prev, { id: logId, type: 'tts', message: `Friday voice output active.`, timestamp: timeStr }]);
          break;
        case 'tts_finished':
          setCurrentState('idle');
          break;
        case 'confirm_required':
          setCurrentState('thinking');
          setActiveConfirmRequest({
            id: confirmationId,
            toolName,
            arguments: toolArgs,
            description: toolQuestion,
          });
          setActivityLogs(prev => [...prev, { 
            id: logId, 
            type: 'confirm', 
            message: `Tool action [${toolName}] requires explicit authorization.`, 
            timestamp: timeStr,
            meta: JSON.stringify(toolArgs)
          }]);
          break;
        case 'tool_executed':
          setCurrentState('idle');
          setActivityLogs(prev => [...prev, { 
            id: logId, 
            type: 'tool', 
            message: data.cancelled
              ? `Tool execution [${toolName || data.id || 'unknown'}] was rejected.`
              : `Tool execution [${toolName || data.id || 'unknown'}] finished.`, 
            timestamp: timeStr,
            meta: data.output || data.result
          }]);
          break;
        case 'hermes_notified':
          setActivityLogs(prev => [...prev, { id: logId, type: 'info', message: data.message || data.output || 'Hermes notification emitted.', timestamp: timeStr }]);
          break;
        case 'system_load':
          setSystemStatus(prev => ({
            ...prev,
            cpuUsage: data.cpuUsage,
            memoryUsage: data.memoryUsage,
            networkLatency: data.networkLatency
          }));
          break;
        case 'error':
          setActivityLogs(prev => [...prev, { id: logId, type: 'error', message: `Error: ${data.message || data.error || data}`, timestamp: timeStr }]);
          break;
        default:
          break;
      }
    };

    fridayClient.addEventListener(handleEvent);

    // Connect WebSocket
    wsInstance = fridayClient.connectWebSocket(
      () => {
        setWsConnected(true);
        setSystemStatus(prev => ({ ...prev, online: true }));
      },
      () => {
        setWsConnected(false);
        setSystemStatus(prev => ({ ...prev, online: false }));
      }
    );

    return () => {
      fridayClient.removeEventListener(handleEvent);
      if (wsInstance) {
        wsInstance.close();
      }
      fridayClient.cleanup();
    };
  }, []);

  // Action handlers
  const handleSendCommand = async (command: string) => {
    if (isSendingCommand) return;
    setIsSendingCommand(true);

    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0];
    const logId = `log-${Date.now()}`;

    // Add user text command to logs
    setActivityLogs(prev => [...prev, { 
      id: logId, 
      type: 'info', 
      message: `User Command: "${command}"`, 
      timestamp: timeStr 
    }]);

    try {
      await fridayClient.sendCommand(command);
    } catch (err) {
      console.error(err);
      setActivityLogs(prev => [...prev, { 
        id: `log-${Date.now()}-err`, 
        type: 'error', 
        message: "Failed to send command to Friday Core.", 
        timestamp: timeStr 
      }]);
    } finally {
      setIsSendingCommand(false);
    }
  };

  const handleConfirmTool = async (requestId: string, confirmed: boolean) => {
    try {
      await fridayClient.confirmTool(requestId, confirmed);
    } catch (err) {
      console.error("Confirmation error", err);
    } finally {
      setActiveConfirmRequest(null);
      setCurrentState('idle');
    }
  };

  const handleToggleVoiceLoop = async (active: boolean) => {
    try {
      await fridayClient.toggleVoiceLoop(active);
      setSystemStatus(prev => ({ ...prev, voiceLoopActive: active }));
      if (!active) {
        setCurrentState('idle');
      }
    } catch (err) {
      console.error("Failed to toggle voice loop", err);
    }
  };

  const handleClearLogs = () => {
    setActivityLogs([]);
  };

  return (
    <div className="dashboard-container">
      {/* Grid Graphic Overlays */}
      <div className="overlay-grid" />
      <div className="scanline-effect" />

      {/* Top Navbar Header */}
      <header className="dashboard-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            background: 'linear-gradient(135deg, var(--color-cyan-pure), var(--color-indigo))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 10px rgba(6,182,212,0.3)'
          }}>
            <Shield size={18} style={{ color: '#ffffff' }} />
          </div>
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '0.05em', color: '#ffffff' }}>
              Friday UI
            </h1>
            <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
              LOCAL CONTROL HUD v1.0
            </span>
          </div>
        </div>

        {/* WebSocket Connection Status Badge */}
        <div className="indicator" style={{
          background: 'rgba(15, 23, 42, 0.5)',
          border: '1px solid var(--border-dim)',
          padding: '6px 14px',
          borderRadius: '20px'
        }}>
          <span className={`dot ${wsConnected ? 'active' : 'error'}`}></span>
          <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
            {wsConnected ? 'WS STREAM: ACTIVE' : 'WS STREAM: DISCONNECTED'}
          </span>
        </div>
      </header>

      {/* Main Grid Dashboard */}
      <main className="dashboard-main">
        {/* Left Column - Control Rail */}
        <section className="panel-left" style={{ gap: '20px', padding: '20px' }}>
          <div style={{ flex: 1 }}>
            <StatusRail status={systemStatus} />
          </div>
          <VoicePanel 
            voiceLoopActive={systemStatus.voiceLoopActive}
            onToggleVoiceLoop={handleToggleVoiceLoop}
            currentState={currentState}
          />
        </section>

        {/* Center Column - Core Orb Visualizer */}
        <section className="panel-center">
          <CoreDisplay 
            currentState={currentState}
            voiceLoopActive={systemStatus.voiceLoopActive}
          />
        </section>

        {/* Right Column - Logs & Memory */}
        <section className="panel-right">
          <MemoryPanel facts={memoryFacts} />
          <ActivityLog logs={activityLogs} onClearLogs={handleClearLogs} />
        </section>
      </main>

      {/* Bottom Column - Command Input Panel */}
      <footer className="dashboard-footer">
        <CommandPanel onSendCommand={handleSendCommand} isLoading={isSendingCommand} />
      </footer>

      {/* Safety Confirmation Gateway Overlay */}
      <ToolConfirmModal 
        request={activeConfirmRequest}
        onConfirm={handleConfirmTool}
      />
    </div>
  );
};

export default App;
