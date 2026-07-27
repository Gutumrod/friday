# Friday for Hermes Build Plan

วันที่: 2026-07-27
สถานะ: ready for implementation
ขอบเขตวันนี้: Phase 0 + Shadow foundation เท่านั้น

## Objective

เริ่มบิ้ว Friday for Hermes แบบไม่ทำให้ Friday stable flow เดิมพัง

วันนี้ยังไม่เปิด Hermes เป็น brain จริง และยังไม่ให้ Hermes execute Friday tools

## Source Of Truth

- `D:\AI-Workspace\projects\friday\docs\FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`
- `D:\AI-Workspace\runtime\hermes-native\workspace\hermes-dashboard-api-for-friday.md`
- `D:\AI-Workspace\projects\friday\AGENTS.md`

## Build Scope

### Phase 0: Probe + Manifest

Add:

- `src/friday/hermes_client.py`
- `audit/HERMES_PHASE0_PROBE_2026-07-27.md`

Implement:

- extract session token from dashboard HTML
- probe `GET /api/health`
- probe `GET /api/status`
- probe `GET /api/model/info`
- probe `GET /api/cron/jobs`
- fetch `GET /openapi.json`
- create in-memory endpoint manifest from live OpenAPI
- mark `/api/ws` as manual runtime route because it is not listed in OpenAPI
- log latency/TTFB without secrets

Do not:

- create kanban tasks
- write files through Hermes
- run git operations through Hermes
- change Friday voice behavior

### Phase 1: Shadow Mode Foundation

Add config:

- `FRIDAY_FOR_HERMES_MODE=off|shadow`
- `HERMES_DASHBOARD_URL=http://127.0.0.1:9119`
- `HERMES_KEEPALIVE_INTERVAL_SECONDS=5`
- `HERMES_SYNC_SOFT_DETACH_SECONDS=20`
- `HERMES_SYNC_HARD_TIMEOUT_SECONDS=60`

Behavior:

- default mode is `off`
- `shadow` sends user text to Hermes non-blocking after STT
- Friday still answers with existing flow
- Hermes response is logged only
- Hermes failure must not affect Friday

Runtime log:

- `vault/hermes_shadow/YYYY-MM-DD.jsonl`

Minimum fields:

- `correlation_id`
- `user_text`
- `mode`
- `context_policy`
- `hermes_ttfb_ms`
- `hermes_total_latency_ms`
- `status`
- `error`

## WebSocket Smoke

Use dashboard WebSocket route:

- `/api/ws`
- JSON-RPC `session.create`
- JSON-RPC `prompt.submit`

Acceptance:

- can submit one short prompt to Hermes
- can receive final text
- timeout returns clean error
- token is never logged

## Test Gate

Run from repo root:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\core.py src\friday\config.py src\friday\hermes_client.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py
```

If UI/API is touched:

```powershell
cd D:\AI-Workspace\projects\friday\ui
npm run build
```

## Acceptance Criteria

- Friday tests still pass
- Hermes probe passes when dashboard is running
- Hermes probe fails gracefully when dashboard is down
- WebSocket smoke gets one response
- `FRIDAY_FOR_HERMES_MODE=off` preserves existing behavior
- `FRIDAY_FOR_HERMES_MODE=shadow` logs Hermes result but does not speak/use it
- no token/secrets in logs
- no generated audio committed

## Stop Line

Stop before implementing:

- sync live responses
- Hermes tool intent execution
- kanban task creation from Friday
- git/filesystem writes through Hermes
- result read interrupt
- public packaging

## Next Decision After This Build

After Phase 0 + Shadow passes, decide whether to enable `sync` for speak-only, non-side-effect requests.

