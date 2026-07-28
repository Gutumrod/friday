# Friday Development Plan Refresh

วันที่: 2026-07-28
repo: `D:\AI-Workspace\projects\friday`
branch: `master`
current remote head verified: `1e67fbf docs: add optional second brain project reporter phase`

## Current Position

Friday is still the voice runtime, safety gateway, and local tool executor.
Hermes is the reasoning/worker router. The integration must stay progressive:
`off` -> `shadow` -> speak-only `sync` -> validated `tool_intent` -> async job UX.

The current stable rule remains:

- `FRIDAY_FOR_HERMES_MODE=off` is the default.
- `shadow` is fire-and-forget only.
- Hermes output is log-only in shadow mode.
- Friday must not speak Hermes output, execute Hermes-sourced tools, change Confirm Gate, write files/git through Hermes, or create Kanban tasks yet.
- Any tool with real-world side effects remains controlled by Friday's existing `CONFIRM_GATED`.

## Verified Source State

- Latest handoff read:
  - `handoff/2026-07-27-friday-hermes-next-session-brief.md`
  - `handoff/2026-07-27-friday-hermes-phase0-review.md`
- Latest core plans read:
  - `docs/FRIDAY_FOR_HERMES_BUILD_PLAN_2026-07-27.md`
  - `docs/FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`
  - `docs/VOICE_LATENCY_ROADMAP_2026-07-19.md`
- Git remote checked and fast-forwarded:
  - `origin https://github.com/Gutumrod/friday.git`
  - pulled `1e67fbf`, which adds optional Second Brain Project Reporter as a future phase.

## What Is Done

### Voice Latency Foundation

- Structured latency logging exists in `src/friday/latency.py`.
- Voice-loop latency logs write to ignored `vault/latency/YYYY-MM-DD.jsonl`.
- Startup phrase bank and selected cached phrases are wired.
- `look_camera` has safe pre-tool progress phrasing; fast read-only tools intentionally stay silent.
- Current blocker for marking latency Phase 0/1 done is missing real spoken baseline: 10-20 spoken turns with median/p95 summary.

### Friday For Hermes Phase 0 + Shadow Foundation

- `src/friday/hermes_client.py` exists.
- Hermes dashboard probing and OpenAPI-derived manifest are implemented.
- Dashboard WebSocket `/api/ws` JSON-RPC smoke path is represented:
  `session.create` -> `prompt.submit`.
- Shadow scheduling exists through `maybe_shadow_hermes_user_text()`.
- Shadow mode is exact-match gated by `FRIDAY_FOR_HERMES_MODE=shadow`.
- Response body/token redaction tests were added.
- `notify_hermes` remains confirm-gated.
- Phase 0 + shadow foundation was committed and pushed in prior work:
  - `f286b92 feat: add Hermes phase0 shadow foundation`
  - `2e55275 docs: add Friday Hermes next session brief`

### Optional Future Feature

- `docs/FRIDAY_FOR_HERMES_PLAN_2026-07-26.md` now includes Phase 6:
  Optional Second Brain Project Reporter.
- This is future optional, disabled by default, config-driven, and read-only first.
- It must not hard-code `Gutumrod/second-brain-vault` or local machine paths.

## Current Risks / Unknowns

- Full `src/test_tools.py` recently timed out around live JaiTTS/F5-TTS dependency work.
  Do not treat this as a Hermes regression without rerunning under stable live dependencies
  or isolating non-live tests.
- Hermes dashboard tokens are ephemeral. Never persist or log them.
- Dashboard/API availability is machine-runtime state. Re-probe before relying on sync behavior.
- Mac portability is not done. Windows-only parts remain: `ctypes.windll`, PowerShell clipboard,
  Task Scheduler, batch launchers, and JaiTTS/F5-TTS runtime validation.
- JaiTTS Colab evidence is benchmark/reference only, not a Friday runtime dependency.

## Updated Phase Plan

### Phase A: Evidence Collection For Shadow Mode

Status: next recommended phase

Goal:

- prove shadow mode is safe and useful before Friday speaks or acts on Hermes output.

Work:

- run Friday with `FRIDAY_FOR_HERMES_MODE=shadow`
- capture 5-10 real spoken user turns
- inspect `vault/hermes_shadow/YYYY-MM-DD.jsonl`
- confirm each row has:
  - `correlation_id`
  - mode/status
  - latency/TTFB fields where available
  - no raw response body
  - no dashboard token, Bearer token, or secret-like values
- summarize whether Hermes responses are useful enough for speak-only sync.

Acceptance:

- Friday voice behavior is unchanged while shadow is on.
- Hermes failures do not interrupt Friday.
- shadow logs are redacted and operationally useful.
- owner can approve or reject moving to speak-only sync from evidence.

### Phase B: Finish Latency Baseline

Status: next recommended phase, can run alongside Phase A

Goal:

- turn latency work from "implemented" into measured.

Work:

- collect 10-20 real spoken turns under normal use
- summarize median/p95:
  - STT
  - LLM/tool routing
  - TTS generation
  - first audio
  - total turn latency
- classify bottlenecks by `path_type`.

Acceptance:

- `docs/VOICE_LATENCY_ROADMAP_2026-07-19.md` can mark Phase 0 baseline complete.
- Phase 1 low-risk wins have before/after or at least after-baseline evidence.
- next optimization is chosen from measured bottleneck, not feeling.

### Phase C: Speak-Only Sync MVP

Status: blocked until Phase A is approved

Goal:

- let Friday ask Hermes for non-side-effect answers without handing over tool execution.

Work:

- add `FRIDAY_FOR_HERMES_MODE=sync`
- allowlist only safe non-side-effect intent classes
- Hermes may return `speak` only
- use keep-alive every 5 seconds, soft detach around 20 seconds, hard foreground wait around 60 seconds
- fallback cleanly to current Friday flow on connection/hard-timeout errors.

Acceptance:

- one Hermes-backed voice question works.
- normal 20-30 second Hermes thinking does not create dead air.
- timeout/detach preserves `correlation_id`.
- no stack traces or raw backend errors are spoken.
- no tools execute from Hermes output.

### Phase D: Tool Intent Bridge

Status: future, do not start before speak-only sync proves stable

Goal:

- allow Hermes to suggest tool calls while Friday remains the safety executor.

Work:

- Hermes returns `tool_intent`.
- Friday validates against `TOOL_SCHEMAS`.
- malformed intents get structured `schema_error`.
- retry limit stays `MAX_TOOL_INTENT_RETRIES=2`.
- existing `CONFIRM_GATED` decides whether user approval is required.

Acceptance:

- one ungated tool intent works.
- one gated tool intent asks confirmation and executes only after confirm.
- negative confirm cancels.
- tests cover unknown tool, schema failure, retry exhaustion, gated tool, and timeout.

### Phase E: Async Job UX

Status: future

Goal:

- make long Hermes/agent jobs voice-friendly without blocking Friday.

Work:

- durable async mailbox with `correlation_id` / task id
- short spoken acknowledgement
- later status query
- saved result report
- interrupt for long result readout

Acceptance:

- long jobs do not block the voice loop.
- user can ask for status later.
- Friday can summarize late Hermes results.
- stopping spoken summary does not lose the result.

### Phase F: Serious JaiTTS Quality Benchmark

Status: future, useful before changing long-answer TTS architecture

Goal:

- decide voice-quality improvements from real local benchmark evidence.

Work:

- fixed set of at least 30 Friday-real utterances
- compare current JaiTTS, chunking variants, reference-audio variants, and edge-tts fallback
- record CUDA/env, generation time, and listening verdict
- keep generated audio out of git unless explicitly approved.

Acceptance:

- compact report under `audit/` or `docs/`
- clear verdict: adopt, retry with constraints, or reject
- no runtime architecture change based only on Colab/reference assumptions.

### Phase G: Optional Second Brain Project Reporter

Status: future optional feature, after Hermes MVP is stable

Goal:

- let Friday/Hermes answer project-status questions from a user-owned markdown vault.

Rules:

- disabled by default
- config-driven path/repo only
- read-only first
- no hard-coded owner repo/path
- no writeback without explicit approval

Acceptance:

- `SECOND_BRAIN_ENABLED=false` fully disables it.
- a local markdown vault can produce a short voice-safe project report.
- longer report is stored as an artifact path.
- no vault docs are modified without direct instruction.

## Recommended Next Action

Do Phase A and Phase B together:

1. run Friday in shadow mode
2. speak 5-10 normal turns
3. keep latency logging on
4. inspect both `vault/hermes_shadow/YYYY-MM-DD.jsonl` and `vault/latency/YYYY-MM-DD.jsonl`
5. write a short evidence report

Do not start `sync`, `tool_intent`, Kanban, or Second Brain integration until this evidence exists and owner approves the next phase.

