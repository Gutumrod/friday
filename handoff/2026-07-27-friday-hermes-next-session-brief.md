# Friday for Hermes - Next Session Brief

วันที่: 2026-07-27
repo: `D:\AI-Workspace\projects\friday`
branch: `master`
remote: `https://github.com/Gutumrod/friday`

## Current Git State

- Phase 0 + shadow foundation committed and pushed:
  - `f286b92 feat: add Hermes phase0 shadow foundation`
- Previous local docs checkpoint also pushed in the same push range:
  - `96af1cd docs: add Friday Hermes build handoff briefs`
- `origin/master` was updated from `173b50c` to `f286b92`.

## Source Of Truth For Next Agent

Read these first, in this order:

1. `AGENTS.md`
2. `handoff/2026-07-27-friday-hermes-phase0-shadow-foundation.md`
3. `handoff/2026-07-27-friday-hermes-phase0-review.md`
4. `audit/HERMES_PHASE0_PROBE_2026-07-27.md`
5. `docs/FRIDAY_FOR_HERMES_BUILD_PLAN_2026-07-27.md`
6. `docs/FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`

## What Is Done

- Added `src/friday/hermes_client.py`
  - probes Hermes dashboard
  - extracts ephemeral dashboard session token
  - builds OpenAPI-derived endpoint manifest
  - records `/api/ws` as manual runtime WebSocket route
  - supports one JSON-RPC smoke path: `session.create` -> `prompt.submit`
  - writes shadow metadata logs without raw token or full Hermes response body
- Added config defaults in `src/friday/config.py`
  - `FRIDAY_FOR_HERMES_MODE=off` remains the default
  - shadow log path: `vault/hermes_shadow/YYYY-MM-DD.jsonl`
- Added `maybe_shadow_hermes_user_text()` in `src/friday/core.py`
  - only schedules Hermes when mode is exactly `shadow`
  - fire-and-forget only
  - Hermes output is not used for speech or tools
- Added tests in `src/test_tools.py` for default-off, scheduling, response-body redaction, and error redaction.
- Added `.env.example` and Phase 0 audit artifacts.

## Verified Before Commit

- `git fetch --all --prune`: passed
- `py_compile`: passed for `src/friday/core.py`, `src/friday/config.py`, `src/friday/hermes_client.py`
- `src/test_api.py`: passed 2/2
- `git diff --check`: passed with only LF -> CRLF warnings
- Targeted runtime checks:
  - default mode was `off`
  - `maybe_shadow_hermes_user_text()` did not schedule while off
  - `notify_hermes` remained in `CONFIRM_GATED`
  - redaction removed `token=` / `Bearer` secret-like values in the checked case

## Known Test Caveat

`src/test_tools.py` full suite did not complete during review because live dependencies were unstable:

- timed out after 5 minutes
- stopped only the process started for the test
- stage shown by unbuffered log: live JaiTTS/F5-TTS generation after `Download Vocos from huggingface charactr/vocos-mel-24khz`, `Converting audio...`, `Generating audio in 1 batches...`
- prior live noise in the same run: Ollama API 500 x3 and Google Cloud STT quota exceeded fallback

Do not treat this as a Hermes regression without rerunning or isolating the live dependency.

## Stop Line Still Active

Do not implement yet without owner approval:

- `sync` mode
- Hermes response as live speech
- Hermes `tool_intent`
- Friday executing Hermes-sourced tools
- Confirm Gate changes
- Hermes filesystem/git writes
- Kanban task creation through Hermes

## Recommended Next Step

Phase 1 evidence collection:

1. Run Friday with `FRIDAY_FOR_HERMES_MODE=shadow` only.
2. Capture 5-10 real user turns.
3. Inspect `vault/hermes_shadow/YYYY-MM-DD.jsonl`.
4. Verify each row has `correlation_id`, status, latency, and no raw response body/token.
5. Only after that, decide whether to build speak-only `sync` mode for non-side-effect requests.
