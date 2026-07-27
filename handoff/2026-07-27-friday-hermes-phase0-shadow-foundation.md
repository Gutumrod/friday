# Handoff - Friday for Hermes Phase 0 + Shadow Foundation

วันที่: 2026-07-27
ผู้เขียน: Codex
repo: `D:\AI-Workspace\projects\friday`
branch: `master`

## สรุปสั้น

เริ่ม implement Friday for Hermes ตาม brief/build plan เฉพาะ Phase 0 + Phase 1 shadow foundation แล้ว โดยยังไม่เปลี่ยน UX เดิมของ Friday, ยังไม่ให้ Hermes execute tool, ไม่แตะ Confirm Gate, และยังไม่ commit/push เพราะ brief ระบุให้หยุดก่อน commit/push เพื่อรอ approval.

## Source Of Truth ที่อ่านแล้ว

- `docs/FRIDAY_FOR_HERMES_MULTI_AGENT_BRIEF_2026-07-27.md`
- `docs/FRIDAY_FOR_HERMES_BUILD_PLAN_2026-07-27.md`
- `docs/FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`
- `D:\AI-Workspace\runtime\hermes-native\workspace\hermes-dashboard-api-for-friday.md`
- `AGENTS.md`
- `handoff/2026-07-26-jaitts-colab-serious-voice-plan.md`
- `handoff/2026-07-26-friday-for-hermes-product-plan.md`

## Git / Repo State

- `git status --short` was clean before edits.
- current branch: `master`
- remote: `origin https://github.com/Gutumrod/friday.git`
- `git fetch --all --prune` completed before edits.
- no branch alternatives found beyond `origin/master`.

## Files Changed

- `src/friday/hermes_client.py`
  - new Hermes dashboard client
  - extracts ephemeral session token from dashboard HTML
  - probes REST endpoints
  - builds in-memory endpoint manifest from live OpenAPI
  - marks `/api/ws` as manual runtime route
  - submits one WebSocket prompt through JSON-RPC `session.create` -> `prompt.submit`
  - writes shadow metadata log without token or full response body

- `src/friday/config.py`
  - added Friday for Hermes config/env defaults
  - default `FRIDAY_FOR_HERMES_MODE=off`
  - dashboard default `http://127.0.0.1:9119`

- `src/friday/core.py`
  - added `maybe_shadow_hermes_user_text()`
  - schedules Hermes shadow request only when mode is `shadow`
  - call is fire-and-forget after user text is logged
  - no Hermes result is used for speech or tool execution

- `src/test_tools.py`
  - added checks for default-off behavior
  - added shadow scheduling check
  - added log redaction check
  - added error redaction check

- `.env.example`
  - documents local env/config with no real secrets

- `audit/HERMES_PHASE0_PROBE_2026-07-27.md`
  - human-readable probe report

- `audit/hermes_phase0_probe_2026-07-27.json`
  - machine-readable Phase 0 probe evidence

## Verified

- `py_compile` passed:
  - `src/friday/core.py`
  - `src/friday/config.py`
  - `src/friday/hermes_client.py`

- `src/test_api.py`: 2/2 passed.
- `src/test_tools.py`: passed once at 79/79 after implementation.
- After redaction hardening, a full rerun of `src/test_tools.py` timed out after 20 minutes on a live dependency; the stuck `src\test_tools.py` process was verified by command line and stopped.
- Targeted Hermes checks after the redaction patch passed.
- `git diff --check` passed; only Windows CRLF warnings were printed.
- Secret scan over `.env.example` and audit artifacts found no raw token/Bearer/session-token leak.

## Hermes Phase 0 Live Evidence

- Dashboard URL: `http://127.0.0.1:9119`
- Dashboard HTML returned 200 and contained a session token.
- Token was not persisted; evidence stores only token presence and length.
- `/api/health`: 200
- `/api/status`: 200
- `/api/model/info`: 200
- `/api/cron/jobs`: 200
- `/openapi.json`: 200
- OpenAPI document version: `3.1.0`
- Hermes API version: `0.19.0`
- OpenAPI path count: 248
- `/api/ws` is not listed in OpenAPI and is recorded as manual runtime route.
- WebSocket smoke response preview: `READY`
- WebSocket smoke used token-redacted URL and JSON-RPC flow `session.create` -> `prompt.submit`.
- Smoke total latency was about 32.2 seconds, consistent with expected Hermes thinking latency.

## Current Stop Line

Do not commit/push yet unless the owner approves.

Do not proceed to:

- `sync` mode
- Hermes speak-live response
- Hermes `tool_intent`
- Friday executing Hermes-sourced tools
- Confirm Gate changes
- Hermes filesystem/git writes

## Recommended Next Step

1. Codex reviews current diff.
2. Decide whether to commit/push Phase 0 + shadow foundation.
3. If approved, run a clean final `test_tools.py` when live dependencies are stable, then commit/push.
4. Next implementation should still stay in shadow evidence collection before any sync/live response behavior.
