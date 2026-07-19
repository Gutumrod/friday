---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-19-friday-ui-plan-refresh-and-live-api-verification.md
วันที่: 2026-07-19
ผู้เขียน: Codex
---

# Handoff - Friday UI plan refresh and live API verification

## สรุป

ต่อจาก `handoff/2026-07-19-tv-connect-preflight-and-startup-live-test.md`

ผู้ใช้สั่งให้อัปเดตความคืบหน้าแล้วทำต่อ จึงทำสองส่วน:

1. อัปเดตเอกสารแผนให้ตรงกับสถานะจริง
2. ทำ live verification ของ Friday API/UI v1

## ไฟล์ที่แก้/เพิ่ม

- `docs/VOICE_LATENCY_ROADMAP_2026-07-19.md`
- `docs/FRIDAY_UI_IMPLEMENTATION_PLAN.md`
- `ui/src/api/fridayClient.ts`
- `run_friday_api.bat`
- `handoff/2026-07-19-friday-ui-plan-refresh-and-live-api-verification.md`

## Progress Update

Voice latency roadmap:

- Phase 0 ยังเป็น `in progress` เพราะยังขาด spoken baseline 10-20 turns
- Phase 1 ยังเป็น `in progress` เพราะยังต้องรอ before/after metric จาก Phase 0
- implementation ของ latency logging, phrase bank, startup phrase choreography, `look_camera` progress phrase, และ TV error phrase path ทำแล้ว
- บันทึก commit ล่าสุดที่เกี่ยวกับ TV preflight: `049bc72`

Friday UI plan:

- Phase 1 refactor core: done for v1
- Phase 2 API service: done for v1
- Phase 3 UI dashboard: done for v1 scaffold
- Phase 4 real wiring: mostly done for status/chat/WebSocket/confirm/memory/history
- Phase 5 verification: ผ่าน live API/UI checks รอบนี้แล้ว แต่ยังควรมี browser visual pass เพิ่มก่อนเรียกว่า polished

## Code Fix

แก้ `ui/src/api/fridayClient.ts`:

- `toggleVoiceLoop()` เดิมอ่าน `data.success`
- แต่ API `/api/voice/start` และ `/api/voice/stop` คืน `{ running, message }`
- แก้ให้ตรวจ `data.running` เทียบกับ state ที่ user ต้องการ

เพิ่ม `run_friday_api.bat`:

- ตั้ง `PYTHONPATH=%~dp0src`
- เปิด `uvicorn friday.api:app --host 127.0.0.1 --port 8000`
- เหตุผล: direct `python -m uvicorn friday.api:app` จาก repo root หา package `friday` ไม่เจอถ้าไม่ set `PYTHONPATH`

## Environment Fix

พบ env drift:

- `requirements.txt` มี `websockets==15.0.1` อยู่แล้ว
- แต่ active env `C:\Users\Win10\miniconda3\envs\friday` ไม่มี package นี้
- ทำให้ uvicorn log:
  - `Unsupported upgrade request.`
  - `No supported WebSocket library detected.`
- ติดตั้งแล้ว:
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe -m pip install websockets==15.0.1`

## Validation

ใช้ Python env:

`C:\Users\Win10\miniconda3\envs\friday\python.exe`

ผล:

- `python -m py_compile src\friday\core.py src\friday\api.py src\test_tools.py src\test_api.py` passed
- `src\test_api.py`: 2 tests OK
- `src\test_tools.py`: 76/76 passed
- `ui`: `npm run build` passed
- Vite dev server:
  - `http://127.0.0.1:3000/` returned HTTP 200
- API direct:
  - `/api/status` returned `status=ok`, `tool_count=29`
  - `/api/tools` returned 29 tools, 21 confirm-gated
  - `/api/voice/start` returned `running=true`
  - `/api/voice/stop` returned `running=false`
- API through Vite proxy:
  - `http://127.0.0.1:3000/api/status` returned `status=ok`
- WebSocket:
  - `ws://127.0.0.1:8000/ws/events` returned snapshot
  - `ws://127.0.0.1:3000/ws/events` through Vite proxy returned snapshot
- `/api/chat` live:
  - input `ตอนนี้กี่โมง`
  - model called `get_time`
  - reply returned current time
- confirm gate live:
  - input `เปิด notepad ให้หน่อย`
  - API returned pending confirmation for `open_app` with args `notepad`
  - cancelled via `/api/tool/confirm`
  - returned `ยกเลิกการเปิด notepad แล้วค่ะ`, `executed=false`
- Browser visual pass:
  - opened `http://127.0.0.1:3000/` with Playwright/Chrome
  - title visible
  - model text visible
  - command `เปิด notepad ให้หน่อย` opened confirm modal
  - confirm modal showed `open_app` and `ต้องการเปิด notepad`
  - `Reject Action` closed modal
  - no page errors
  - screenshot saved at runtime path `output/playwright/friday-ui-live.png`
  - initial pass observed one transient console warning for `ws://127.0.0.1:3000/ws/events`
  - root cause was React `StrictMode` cleanup closing a WebSocket while it was still connecting
  - fixed `fridayClient.connectWebSocket()` so cleanup during `CONNECTING` defers close until `onopen`
  - rerun browser pass showed no WebSocket warning and no page errors

Known warnings เดิม:

- Google Cloud STT quota exceeded during fallback tests, but tests passed
- Google API Python 3.10 future support warning
- HuggingFace unauthenticated warning
- mocked/corrupt audio warnings from existing tests

## Runtime State

- Vite dev server may still be listening on `127.0.0.1:3000` from live verification
- API was tested in temporary/in-process uvicorn for the final WebSocket pass
- `vault/` logs are runtime ignored and should not be committed
- `output/` is ignored; Playwright screenshots are runtime artifacts and should not be committed

## Next Work

1. Collect 10-20 real spoken turns for voice latency Phase 0/1 metrics
2. TV/YouTube debug remains blocked on finding the real current LG TV IP
3. UI polish follow-up:
   - consider adding a small visible connection state for backend WebSocket health separate from Vite HMR
   - do a longer manual dashboard session after real voice baseline collection
