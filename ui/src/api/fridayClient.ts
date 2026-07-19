/**
 * Friday API Client
 * 
 * NOTE: Phase 4 connects this client to the real Friday FastAPI backend.
 * Mock implementations remain in this file only as a local fallback switch.
 */

export const USE_MOCK = false;

export interface SystemStatus {
  online: boolean;
  model: string;
  micConnected: boolean;
  sttEngine: string;
  ttsEngine: string;
  hermesConnected: boolean;
  networkLatency: number;
  voiceLoopActive: boolean;
  cpuUsage: number;
  memoryUsage: number;
}

export interface MemoryFact {
  id: string;
  category: string;
  content: string;
  timestamp: string;
}

export interface ActivityLogItem {
  id: string;
  type: 'info' | 'listening' | 'stt' | 'thinking' | 'llm' | 'tool' | 'confirm' | 'tts' | 'error';
  message: string;
  timestamp: string;
  meta?: string;
}

export interface ToolCallRequest {
  id: string;
  toolName: string;
  arguments: Record<string, any>;
  description: string;
}

export type EventCallback = (eventType: string, data: any) => void;

interface BackendStatus {
  status?: string;
  service?: string;
  model?: string;
  voice_running?: boolean;
  pending_confirmations?: number;
  tool_count?: number;
}

interface BackendEvent {
  id?: string;
  type?: string;
  created_at?: string;
  payload?: Record<string, any>;
  data?: Record<string, any>;
  events?: BackendEvent[];
}

class FridayClient {
  private wsListeners: Set<EventCallback> = new Set();
  private mockInterval: number | null = null;
  private wsConnected: boolean = false;

  constructor() {
    if (USE_MOCK) {
      this.startMockEventLoop();
    }
  }

  // --- Core API Methods ---

  async getStatus(): Promise<SystemStatus> {
    if (USE_MOCK) {
      return {
        online: true,
        model: "Gemini 1.5 Flash (fallback to Llama3)",
        micConnected: true,
        sttEngine: "Google STT",
        ttsEngine: "JaiTTS (Thai)",
        hermesConnected: true,
        networkLatency: 45, // ms
        voiceLoopActive: false,
        cpuUsage: 12,
        memoryUsage: 42,
      };
    }
    
    const res = await fetch('/api/status');
    if (!res.ok) {
      throw new Error(`GET /api/status failed: ${res.status}`);
    }
    const data: BackendStatus = await res.json();
    return {
      online: data.status === 'ok',
      model: data.model || 'Unknown',
      micConnected: false,
      sttEngine: 'Google STT',
      ttsEngine: 'JaiTTS',
      hermesConnected: true,
      networkLatency: 0,
      voiceLoopActive: Boolean(data.voice_running),
      cpuUsage: 0,
      memoryUsage: 0,
    };
  }

  async getMemoryFacts(): Promise<MemoryFact[]> {
    if (USE_MOCK) {
      return [
        { id: "1", category: "User Info", content: "User is 'คุณฟรี' (CEO / Executive)", timestamp: "2026-07-17 12:00:00" },
        { id: "2", category: "Preferences", content: "Prefers concise summary tables, dislikes over-politeness", timestamp: "2026-07-17 12:05:00" },
        { id: "3", category: "Preferences", content: "Daughter is top priority. Safe tool confirmation must be enabled", timestamp: "2026-07-17 12:10:00" },
        { id: "4", category: "Devices", content: "LG TV at IP 192.168.1.55, Sony Camera on USB-1", timestamp: "2026-07-17 14:22:00" },
        { id: "5", category: "Hermes", content: "Hermes mailbox directory monitored at D:/AI-Workspace/mailbox", timestamp: "2026-07-17 15:40:00" },
      ];
    }

    const res = await fetch('/api/memory/facts');
    if (!res.ok) {
      throw new Error(`GET /api/memory/facts failed: ${res.status}`);
    }
    const data: { facts?: string | MemoryFact[] } = await res.json();
    if (Array.isArray(data.facts)) {
      return data.facts;
    }
    return this.parseFactsMarkdown(data.facts || '');
  }

  async getActivityLogs(): Promise<ActivityLogItem[]> {
    if (USE_MOCK) {
      return [
        { id: "log-1", type: "info", message: "Friday UI Dashboard initialized.", timestamp: "19:53:00" },
        { id: "log-2", type: "info", message: "Connected to Friday Core Service Loop.", timestamp: "19:53:01" },
        { id: "log-3", type: "tool", message: "Scanned Hermes mailbox inbox: 0 pending tasks.", timestamp: "19:53:05", meta: "mailbox/inbox/antigravity/" },
        { id: "log-4", type: "info", message: "Voice loop in standby mode. Ready to receive commands.", timestamp: "19:53:10" }
      ];
    }

    const res = await fetch('/api/history/latest');
    if (!res.ok) {
      throw new Error(`GET /api/history/latest failed: ${res.status}`);
    }
    const data: { path?: string | null; content?: string } = await res.json();
    return this.parseHistoryMarkdown(data.content || '', data.path || undefined);
  }

  async sendCommand(text: string): Promise<string> {
    if (USE_MOCK) {
      this.triggerEvent('thinking_started', {});
      
      // Simulate thinking and response delay
      return new Promise((resolve) => {
        setTimeout(() => {
          let responseText = `I have received your request: "${text}". I am currently running in mock mode, but I can process commands.`;
          
          // Custom mock triggers to simulate tool confirmations
          if (text.toLowerCase().includes("tv") || text.toLowerCase().includes("ทีวี") || text.toLowerCase().includes("เปิดทีวี")) {
            this.triggerEvent('confirm_required', {
              id: `req-${Date.now()}`,
              toolName: "tv.turn_on",
              arguments: { ip: "192.168.1.55", app: "YouTube" },
              description: "Turn on LG OLED TV in Living Room and launch YouTube."
            });
            responseText = "Requesting permission to run LG TV power control...";
          } else if (text.toLowerCase().includes("camera") || text.toLowerCase().includes("กล้อง") || text.toLowerCase().includes("ถ่ายรูป")) {
            this.triggerEvent('confirm_required', {
              id: `req-${Date.now()}`,
              toolName: "camera.capture",
              arguments: { resolution: "4K", autofocus: true },
              description: "Trigger Sony DSLR Camera to capture image via USB-1."
            });
            responseText = "Awaiting camera trigger permission confirmation...";
          } else {
            this.triggerEvent('llm_response', { text: responseText });
            this.triggerEvent('tts_started', { text: responseText });
            setTimeout(() => this.triggerEvent('tts_finished', {}), 1500);
          }
          
          resolve(responseText);
        }, 1200);
      });
    }

    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    if (!res.ok) {
      throw new Error(`POST /api/chat failed: ${res.status}`);
    }
    const data = await res.json();
    return data.reply || '';
  }

  async confirmTool(requestId: string, confirmed: boolean): Promise<boolean> {
    if (USE_MOCK) {
      return new Promise((resolve) => {
        setTimeout(() => {
          if (confirmed) {
            this.triggerEvent('tool_executed', { id: requestId, status: "success", result: "Action completed successfully" });
          } else {
            this.triggerEvent('tool_executed', { id: requestId, status: "cancelled", result: "Rejected by User" });
          }
          resolve(true);
        }, 800);
      });
    }

    const res = await fetch('/api/tool/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirmation_id: requestId, confirm: confirmed })
    });
    if (!res.ok) {
      throw new Error(`POST /api/tool/confirm failed: ${res.status}`);
    }
    const data = await res.json();
    return typeof data.executed === 'boolean' ? data.executed : true;
  }

  async toggleVoiceLoop(active: boolean): Promise<boolean> {
    if (USE_MOCK) {
      if (active) {
        this.triggerEvent('listening_started', {});
        // Mock a user speech after 3 seconds
        setTimeout(() => {
          this.triggerEvent('stt_result', { text: "สวัสดี Friday เปิดทีวีให้หน่อย" });
          this.sendCommand("สวัสดี Friday เปิดทีวีให้หน่อย");
        }, 4000);
      } else {
        this.triggerEvent('tts_finished', {});
      }
      return true;
    }

    const endpoint = active ? '/api/voice/start' : '/api/voice/stop';
    const res = await fetch(endpoint, { method: 'POST' });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(`POST ${endpoint} failed: ${res.status}`);
    }
    return Boolean(data.running) === active;
  }

  // --- WebSocket Simulation & Event Dispatcher ---

  connectWebSocket(onOpen: () => void, onClose: () => void) {
    if (USE_MOCK) {
      setTimeout(() => {
        this.wsConnected = true;
        onOpen();
        this.triggerEvent('info', 'WebSocket Connection Established (Mock Mode)');
      }, 500);
      return {
        close: () => {
          this.wsConnected = false;
          onClose();
        }
      };
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/events`);
    ws.onopen = onOpen;
    ws.onclose = onClose;
    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      this.handleBackendEvent(parsed);
    };
    return ws;
  }

  addEventListener(callback: EventCallback) {
    this.wsListeners.add(callback);
  }

  removeEventListener(callback: EventCallback) {
    this.wsListeners.delete(callback);
  }

  private triggerEvent(type: string, data: any) {
    this.wsListeners.forEach(listener => {
      try {
        listener(type, data);
      } catch (err) {
        console.error("Error in WS Listener: ", err);
      }
    });
  }

  private handleBackendEvent(event: BackendEvent) {
    if (event.type === 'snapshot') {
      (event.events || []).forEach((snapshotEvent) => this.handleBackendEvent(snapshotEvent));
      return;
    }
    if (!event.type) return;
    this.triggerEvent(event.type, event.payload ?? event.data ?? {});
  }

  private parseFactsMarkdown(markdown: string): MemoryFact[] {
    const lines = markdown.split(/\r?\n/);
    const facts: MemoryFact[] = [];
    let category = 'Memory';
    let buffer: string[] = [];

    const flush = () => {
      const content = buffer.join('\n').trim();
      if (!content) return;
      facts.push({
        id: `fact-${facts.length + 1}`,
        category,
        content,
        timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19),
      });
      buffer = [];
    };

    for (const line of lines) {
      if (line.startsWith('## ')) {
        flush();
        category = line.replace(/^##\s+/, '').trim() || 'Memory';
      } else if (!line.startsWith('# ')) {
        buffer.push(line);
      }
    }
    flush();
    return facts;
  }

  private parseHistoryMarkdown(markdown: string, path?: string): ActivityLogItem[] {
    if (!markdown.trim()) {
      return [];
    }
    const entries = markdown.split(/^###\s+/m).filter(Boolean);
    return entries.map((entry, index) => {
      const [header = '', ...bodyLines] = entry.split(/\r?\n/);
      const timeMatch = header.match(/(\d{2}:\d{2}:\d{2})/);
      const role = header.includes('นาย') || header.toLowerCase().includes('user') ? 'info' : 'llm';
      return {
        id: `history-${index}`,
        type: role,
        message: bodyLines.join('\n').trim() || header.trim(),
        timestamp: timeMatch?.[1] || '--:--:--',
        meta: path,
      };
    });
  }

  // Mock Event Loop to create ambient background events
  private startMockEventLoop() {
    this.mockInterval = window.setInterval(() => {
      if (!this.wsConnected) return;

      const rand = Math.random();
      if (rand < 0.05) {
        // Random CPU/Memory usage update
        this.triggerEvent('system_load', {
          cpuUsage: Math.floor(Math.random() * 20) + 5,
          memoryUsage: 40 + Math.floor(Math.random() * 5),
          networkLatency: 30 + Math.floor(Math.random() * 30)
        });
      } else if (rand < 0.07) {
        // Mock occasional background scanning of Hermes mailbox
        this.triggerEvent('hermes_notified', {
          message: "Hermes inbox scanned: No new external messages."
        });
      }
    }, 4000);
  }

  cleanup() {
    if (this.mockInterval) {
      clearInterval(this.mockInterval);
      this.mockInterval = null;
    }
  }
}

export const fridayClient = new FridayClient();
