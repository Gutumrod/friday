# Hermes Phase 0 Probe - Friday for Hermes

วันที่: 2026-07-27
ผู้รัน: Codex
repo: `D:\AI-Workspace\projects\friday`

## Scope

Phase 0 + Phase 1 Shadow foundation only.

ไม่มีการให้ Hermes execute tool, ไม่มี kanban task, ไม่มี git/filesystem write ผ่าน Hermes, และไม่แตะ confirm gate.

## Commands

```powershell
$env:PYTHONPATH='D:\AI-Workspace\projects\friday\src'
C:\Users\Win10\miniconda3\envs\friday\python.exe -m friday.hermes_client --probe --write-audit audit\hermes_phase0_probe_2026-07-27.json
C:\Users\Win10\miniconda3\envs\friday\python.exe -m friday.hermes_client --smoke "ตอบสั้นๆ ว่า READY"
```

## Verified

- Dashboard URL: `http://127.0.0.1:9119`
- Dashboard HTML: 200, session token present, token length 43
- `/api/health`: 200, 1.8 ms
- `/api/status`: 200, 809.7 ms
- `/api/model/info`: 200, 49.5 ms
- `/api/cron/jobs`: 200, 84.0 ms
- `/openapi.json`: 200, 30.7 ms
- OpenAPI document version: 3.1.0
- Hermes API version: 0.19.0
- OpenAPI path count: 248
- `/api/ws` is not listed in OpenAPI and is marked as manual runtime route
- WebSocket smoke used JSON-RPC `session.create` then `prompt.submit`
- WebSocket smoke response: `READY`
- WebSocket smoke TTFB: 53.1 ms
- WebSocket smoke total latency: 32151.6 ms

## Evidence Files

- `audit/hermes_phase0_probe_2026-07-27.json`

The JSON evidence stores endpoint metadata and manifest details. It does not store the raw Hermes session token.

## Notes

- `python -m friday.hermes_client` requires `PYTHONPATH=D:\AI-Workspace\projects\friday\src` because this repo is not installed as a package.
- The smoke response taking about 32 seconds matches the accepted plan assumption that normal Hermes thinking can take 20-30+ seconds.
- `FRIDAY_FOR_HERMES_MODE=off` remains the default; shadow mode only logs Hermes metadata and does not use Hermes output for speech.
