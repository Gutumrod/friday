# Friday UI Implementation Plan

วันที่: 2026-07-17
ผู้เขียน: Codex
สำหรับ: Claude / agent ถัดไปที่รับงาน Friday

## สรุปสั้น

โปรเจกต์นี้ต้องเรียกว่า **Friday UI** เท่านั้น ไม่ใช้ชื่อ Jarvis ในชื่อระบบ หน้า UI หรือเอกสารใหม่ เว้นแต่เป็นการอ้างถึงของเก่าที่มีอยู่แล้วใน source/history

เป้าหมายคือยกระดับ Friday จาก voice assistant แบบ console/walkie-talkie ให้กลายเป็น local dashboard ที่ควบคุมและมองเห็นสถานะของ Friday ได้จริง โดยไม่รื้อ core เดิมทิ้งในรอบแรก

แนวทางหลัก:

1. เก็บ Friday core เดิมไว้ให้รันได้เหมือนเดิม
2. Refactor ไฟล์ใหญ่ให้เป็นโมดูลก่อน
3. ทำ Friday API Service เป็นสะพานระหว่าง core กับ UI
4. ทำ Friday UI เป็น dashboard จริง ไม่ใช่ mockup หลอก
5. เชื่อม state/tool/memory/Hermes/voice ทีละชั้น

## สถานะล่าสุด ณ 2026-07-19

อัปเดตหลัง commit `049bc72`:

- Phase 1 refactor core: ทำเสร็จระดับใช้งานจริงแล้วใน `src/friday/`; `src/friday_walkie_talkie.py` เป็น compatibility launcher
- Phase 2 API service: ทำเสร็จระดับ v1 แล้วใน `src/friday/api.py`
- Phase 3 UI dashboard: scaffold และเชื่อม client จริงแล้วใน `ui/`
- Phase 4 real wiring: ต่อ `/api/status`, `/api/chat`, `/api/tool/confirm`, `/api/memory/facts`, `/api/history/latest`, `/api/voice/start`, `/api/voice/stop`, และ `/ws/events` แล้ว
- Phase 5 verification: Python tests, UI build, API status, Vite proxy, `/api/chat`, confirm cancel flow, `/ws/events` snapshot, and browser confirm-modal flow verified on 2026-07-19
- API launcher added: `run_friday_api.bat` sets `PYTHONPATH=src` before starting `uvicorn`, because direct `python -m uvicorn friday.api:app` from repo root cannot import the `friday` package without that path.

ข้อจำกัดปัจจุบัน:

- `/api/voice/start` และ `/api/voice/stop` ตอนนี้เป็น state marker สำหรับ UI ยังไม่ start/stop realtime voice loop จริง
- UI ยังมี mock fallback code อยู่ แต่ `USE_MOCK = false` เป็นค่า default
- ต้องรัน live verification ทุกครั้งก่อนถือว่า Friday UI v1 พร้อมใช้จริง เพราะ backend/LLM/tool behavior อาจเปลี่ยนตาม runtime state
- Environment drift found and fixed locally: `requirements.txt` already listed `websockets==15.0.1`, but the active conda env was missing it. Installed it into `C:\Users\Win10\miniconda3\envs\friday` during verification.

## Current State ที่ต้องรู้ก่อนเริ่ม

Source of truth ปัจจุบัน:

- `AGENTS.md` บอกให้เปิด handoff ล่าสุดก่อนเสมอ
- handoff ล่าสุดที่อ่านแล้ว: `handoff/2026-07-19-tv-connect-preflight-and-startup-live-test.md`
- main script ปัจจุบัน: `src/friday_walkie_talkie.py`
- test suite ปัจจุบัน: `src/test_tools.py`
- launcher ปัจจุบัน: `run_friday.bat`

สถานะโดยรวม:

- Friday ไม่ใช่โปรเจกต์ว่าง มี voice loop, tools, memory vault, Hermes notify/dispatch, camera, LG TV control, timers, search, TTS cache, JaiTTS fallback/primary path, confirm-gated tool safety แล้ว
- ปัญหาหลักคือทุกอย่างอยู่ในไฟล์เดียวขนาดใหญ่ ทำให้ต่อ UI หรือแก้ architecture ยาก
- Gemini/OpenAI Realtime ยังไม่ใช่เป้าหมายรอบแรก เพราะ handoff ล่าสุดสรุปว่า pain point ตอนนั้นเป็น mic/STT timing ไม่ใช่การพูดแทรกแบบ realtime
- UI แบบในภาพอ้างอิงควรถูกตีความเป็นแรงบันดาลใจด้าน cockpit/dashboard เท่านั้น ชื่อและ identity ต้องเป็น Friday UI

## Non-Negotiables

- ห้ามเปลี่ยนชื่อเป็น Jarvis UI
- ห้ามทำ dashboard ที่เป็น mock data อย่างเดียวแล้วบอกว่าเสร็จ
- ห้ามรื้อ voice loop เดิมจน `run_friday.bat` ใช้ไม่ได้
- ห้ามลด confirm gate ของ tools ที่มี side effect
- ห้าม hard-code secrets/config ใหม่ลง source
- ห้าม commit/generated runtime junk เช่น `src/tts_cache`, `.env`, `vault`, `voices`, `node_modules`, build output
- ห้าม npm install/build ใต้ Google Drive path
- ถ้า repo มี remote ให้ fetch/check branch ก่อนเริ่มงานใหญ่

## Target Architecture

```
Friday Core Engine
  -> Friday API Service
  -> Friday UI Dashboard
  -> Memory / Tools / Hermes / Voice State
```

ชั้นความรับผิดชอบ:

- Core Engine: STT, TTS, LLM, prompt, tool execution, confirm gate, memory logging
- API Service: expose state/events/commands ให้ UI เรียกได้
- Friday UI: dashboard สำหรับดูสถานะ สั่งงาน confirm tool และอ่าน activity
- Memory/Hermes: ใช้ของเดิมก่อน แล้วค่อยปรับให้เป็น service-friendly

## Phase 1: Refactor Core โดยไม่เปลี่ยนพฤติกรรม

Status: done for v1

เป้าหมาย: แยก `src/friday_walkie_talkie.py` ให้เป็นโมดูล แต่ behavior ต้องเหมือนเดิมมากที่สุด

โครงสร้างที่แนะนำ:

```
src/
  friday/
    __init__.py
    config.py
    audio.py
    stt.py
    tts.py
    llm.py
    memory.py
    prompt.py
    core.py
    tools/
      __init__.py
      system.py
      clipboard.py
      browser.py
      timers.py
      hermes.py
      camera.py
      tv.py
  friday_walkie_talkie.py
  test_tools.py
```

ข้อกำกับ:

- `friday_walkie_talkie.py` ควรกลายเป็น thin launcher ที่เรียก `friday.core.main()` หรือ equivalent
- ย้าย config hard-coded ไป `config.py` ก่อน แล้วค่อยตัดสินใจว่าจะอ่านจาก `.env`/local config เพิ่มอย่างไร
- รักษา public function names ที่ test ใช้อยู่ หรือค่อยๆ ปรับ test พร้อม shim
- อย่าเปลี่ยน prompt/tool schema พร้อมกับ refactor ถ้าไม่จำเป็น
- หลังจบ phase นี้ `run_friday.bat` ต้องยังทำงานได้

Verification:

```
conda activate friday
python src/test_tools.py
python src/friday_walkie_talkie.py
```

Implementation status:

- `config.py`, `memory.py`, `llm.py`, `latency.py`, `phrases.py`, `api.py`, and `core.py` now exist under `src/friday/`
- `src/friday_walkie_talkie.py` remains the launcher path for the old walkie-talkie flow
- Full tools split into subpackages is not done yet; keep it out of scope unless `core.py` size blocks the next feature

## Phase 2: Friday API Service

Status: done for v1

เป้าหมาย: เพิ่ม service ให้ UI คุยกับ Friday ได้โดยไม่ import internals ตรงๆ

แนะนำ dependencies แบบ pin version:

```
fastapi==0.116.1
uvicorn==0.35.0
websockets==15.0.1
pydantic==2.11.7
```

API v1 ที่ควรมี:

```
GET  /api/status
GET  /api/tools
GET  /api/memory/facts
GET  /api/history/latest
POST /api/chat
POST /api/tool/confirm
POST /api/voice/start
POST /api/voice/stop
WS   /ws/events
```

Event types ที่ UI ต้องเห็น:

- `listening_started`
- `stt_result`
- `thinking_started`
- `llm_response`
- `tool_requested`
- `confirm_required`
- `tool_executed`
- `tts_started`
- `tts_finished`
- `hermes_notified`
- `error`

ข้อควรระวัง:

- API รอบแรกไม่จำเป็นต้องทำ realtime audio เต็ม
- `POST /api/chat` อาจเริ่มจาก text command ก่อน
- voice loop เดิมอาจยังเป็น process หลัก แล้ว API เป็นอีก entrypoint ได้ แต่ต้องไม่ทำให้ state ตีกัน

Implementation status:

- Existing endpoints: `/api/status`, `/api/tools`, `/api/memory/facts`, `/api/history/latest`, `/api/chat`, `/api/tool/confirm`, `/api/voice/start`, `/api/voice/stop`, `/ws/events`
- API preserves the existing `CONFIRM_GATED` policy by holding pending confirmations server-side
- Voice start/stop is currently UI-visible state only, not the microphone loop
- Start API on Windows with `run_friday_api.bat`

## Phase 3: Friday UI Dashboard

Status: done for v1 scaffold, browser verification passed

เป้าหมาย: ทำ local web dashboard สำหรับ Friday UI

แนะนำเริ่มเป็น web app ก่อน ยังไม่ต้อง Electron

โครงสร้าง:

```
ui/
  package.json
  vite.config.ts
  index.html
  src/
    App.tsx
    api/
      fridayClient.ts
    components/
      ActivityLog.tsx
      CommandPanel.tsx
      CoreDisplay.tsx
      MemoryPanel.tsx
      StatusRail.tsx
      ToolConfirmModal.tsx
      VoicePanel.tsx
    styles/
      globals.css
```

Dependencies ที่แนะนำให้ pin:

```
@vitejs/plugin-react@4.7.0
vite@7.0.5
react@19.1.0
react-dom@19.1.0
lucide-react@0.468.0
typescript@5.8.3
```

Layout:

- ซ้าย: system status, mic, STT, TTS, model, Hermes, network
- กลาง: Friday Core visual แบบวงกลมหรือ radar-style ใช้ชื่อ Friday ชัดเจน
- ขวา: activity log, tool calls, pending confirmations
- ล่าง: command input, voice waveform/status, start/stop controls

Design note:

- ใช้ mood แบบ sci-fi cockpit ได้ แต่ text/branding ต้องเป็น Friday UI
- หลีกเลี่ยง landing page ให้เปิดมาเป็น dashboard ที่ใช้งานได้ทันที
- อย่าใส่คำอธิบายฟีเจอร์ยาวๆ ในหน้า app
- UI ควรโชว์ state จริงจาก API ตั้งแต่ v1 แม้บาง panel จะยัง read-only

Implementation status:

- UI exists under `ui/` with React/Vite and Friday dashboard components
- `ui/src/api/fridayClient.ts` uses real backend calls by default with `USE_MOCK = false`
- `ToolConfirmModal` is wired to `/api/tool/confirm`
- Browser verification captured screenshot at runtime path `output/playwright/friday-ui-live.png`
- Initial transient browser WebSocket warning was resolved by making the client close wrapper defer cleanup while the socket is still connecting. Latest browser pass shows only normal Vite/React dev console messages and no page errors.
- Remaining work here is polish and sustained-use tightening, not more mock UI

## Phase 4: เชื่อมของจริงทีละส่วน

Status: done for v1 items 1-5, partial for items 6-7

ลำดับที่แนะนำ:

1. UI เรียก `/api/status` แล้วแสดงสถานะจริง
2. UI ส่ง text command ผ่าน `/api/chat`
3. API ส่ง event ผ่าน WebSocket
4. UI แสดง tool call และ confirm gate
5. UI อ่าน memory facts/history จาก vault
6. UI แสดง Hermes notify/dispatch status
7. ค่อยเพิ่ม start/stop voice loop จาก UI

อย่าเริ่มจาก animation สวยอย่างเดียว เพราะจะกลับไปเป็น shell สวยแต่ backend ยังไม่พร้อม

Current item status:

- 1. `/api/status`: wired
- 2. `/api/chat`: wired
- 3. WebSocket events: wired and verified through API direct and Vite proxy
- 4. tool call + confirm gate: wired and verified in browser with `open_app` pending confirmation then reject
- 5. memory facts/history: wired
- 6. Hermes notify/dispatch status: partially represented through events, needs live workflow verification
- 7. voice loop start/stop: state marker only, real audio-loop control not implemented

## Phase 5: Verification Checklist

ก่อนถือว่า Friday UI v1 ใช้ได้:

- `python src/test_tools.py` ผ่าน: verified 2026-07-19, 76/76
- `python src/test_api.py` ผ่าน: verified 2026-07-19, 2 tests OK
- `npm run build` ผ่าน: verified 2026-07-19
- API เปิดได้ผ่าน `run_friday_api.bat` หรือ equivalent `PYTHONPATH=src` uvicorn command: verified with temporary in-process uvicorn
- UI dev server เปิดได้ที่ `http://127.0.0.1:3000/`: verified HTTP 200
- `/api/status` ได้ข้อมูลจริง: verified direct API and through Vite proxy
- ส่ง text command แล้ว LLM ตอบผ่าน core จริง: verified `ตอนนี้กี่โมง` -> `get_time`
- tool ที่มี side effect ยังต้อง confirm ก่อน execute: verified `เปิด notepad ให้หน่อย` -> pending `open_app`, then cancelled without executing
- `/ws/events` ใช้งานได้: verified direct API and Vite proxy snapshot after installing missing `websockets==15.0.1` into the active env
- activity log แสดง event จริง ไม่ใช่ mock ล้วน: backend WebSocket event source verified, browser flow verified confirm modal and reject path
- ไม่มี secret/config ใหม่หลุดเข้า git: check before commit
- ไม่มี runtime/generated junk ถูก add เข้า git: check before commit

## Out of Scope สำหรับรอบแรก

- Gemini Live / OpenAI Realtime migration
- Electron packaging
- Wake word/voiceprint authentication
- full async audio rewrite
- redesign prompt/persona ใหญ่
- rewrite tools ทั้งหมดใหม่

## Recommended First Task for Claude

เริ่มจาก Phase 1 แบบ conservative:

1. อ่าน `AGENTS.md`
2. อ่าน handoff ล่าสุดใน `handoff/`
3. เช็ค `git status`, `git remote -v`, `git fetch --all --prune`
4. รันหรืออย่างน้อย inspect `src/test_tools.py`
5. ทำ refactor แรกเฉพาะ config/memory/llm หรือ tools กลุ่มเล็กก่อน
6. รัน tests
7. เขียน handoff ใหม่บอกว่าแยกอะไรแล้ว behavior เปลี่ยนหรือไม่

ถ้าจะเริ่มเล็กที่สุด แนะนำแยก `config.py`, `memory.py`, `llm.py` ก่อน เพราะเป็น dependency กลางที่ UI/API ต้องใช้ต่อ และยังไม่แตะ hardware/device-heavy tools อย่าง camera/TV/TTS มากเกินไป
