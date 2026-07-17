/**
 * Friday API Client
 * 
 * NOTE: [PHASE 3] CURRENTLY RUNNING IN MOCK MODE.
 * This file contains mock implementations of all APIs and WebSockets.
 * To connect to the real python backend service in Phase 4, toggle the USE_MOCK flag to false.
 */

export const USE_MOCK = true; // TOGGLE THIS FLAG IN PHASE 4 TO CONNECT TO REAL BACKEND

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
    
    // Phase 4 Backend Integration:
    const res = await fetch('/api/status');
    return res.json();
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
    return res.json();
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
    return res.json();
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
      body: JSON.stringify({ command: text })
    });
    const data = await res.json();
    return data.response;
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
      body: JSON.stringify({ id: requestId, confirmed })
    });
    const data = await res.json();
    return data.success;
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
    return data.success;
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

    // Phase 4 Backend Integration:
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/events`);
    ws.onopen = onOpen;
    ws.onclose = onClose;
    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      this.triggerEvent(parsed.type, parsed.data);
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
