---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-26-friday-for-hermes-product-plan.md
วันที่: 2026-07-26
ผู้เขียน: Codex
---

# Handoff - Friday for Hermes product plan

## สรุปสั้น

CEO approved the product direction: build a voice layer for Hermes so Hermes users can talk instead of typing and waiting.

Chosen name:

**Friday for Hermes**

Positioning:

- Friday is the voice runtime, safety gateway, and local tool executor.
- Hermes is the reasoning/worker router and tool manager.
- Mailbox remains the async job queue for long work.
- Ollama remains the model backend behind the scenes.

This is not a plan to replace Friday with Hermes. It is a separation-of-concerns plan that lets Hermes users get a voice interface without removing Friday's confirm gate, transcript, or mailbox safety.

## Files Added

- `docs/FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`

## Source Of Truth Checked

- `AGENTS.md`
- latest handoff: `handoff/2026-07-26-jaitts-colab-serious-voice-plan.md`
- current git remote: `origin https://github.com/Gutumrod/friday.git`
- `git fetch --all --prune` completed before this planning update
- memory quick pass: Friday/Hermes task groups and Windows-native Hermes runtime notes

## Key Design Decision

Use 3 tracks:

1. Fast Track: Friday handles low-latency local/simple commands itself.
2. Sync Delegation: Friday asks Hermes for realtime help only when Hermes has better tools or context.
3. Async Job: Friday creates mailbox tasks for long-running work that should not block voice.

## Safety Rules

- Hermes does not execute Friday tools directly.
- Hermes may return only `speak` or `tool_intent`.
- Friday validates tool intent against its own schemas.
- Friday applies existing `CONFIRM_GATED`.
- Friday keeps transcript and audit trail.
- Every request gets a `correlation_id`.

## Context Window Follow-Up

CEO raised an important risk after approving the plan: Hermes also has an LLM context window because its backend is expected to be DeepSeek through Ollama. The plan now includes a `Context Window Policy`.

Decision:

- Friday keeps the full transcript/audit trail locally.
- Hermes gets bounded intent packets, not full voice transcript dumps.
- Sync Delegation targets small payloads, initially under about 2k tokens.
- Async Job uses standalone task briefs and source paths, not accumulated chat history.
- Requests should log `context_budget_tokens` and `context_policy`.
- `full_debug` context is manual/debug-only, not default voice behavior.

## Voice UX / Timeout Follow-Up

CEO also clarified that Hermes with larger models often needs 20-30 seconds for ordinary work and up to about 60 seconds for longer work. The original 2-5 second timeout is too short for normal Hermes thinking time.

Decision added to the plan:

- Use Progressive Async Handoff instead of a hard short cutoff.
- Friday speaks a neutral acknowledgement immediately after sending to Hermes.
- Friday may speak keep-alive phrases every 5 seconds, up to 3-4 times.
- Around 20 seconds, Friday auto-detaches the Hermes request into background async mode and returns to normal voice conversation.
- When Hermes finishes, Friday queues a result notification and speaks it only at a safe idle moment.
- Keep-alive speech must not imply success, must not replace confirm prompts, and must not speak over `mic_listening`.
- A short 2-5 second timeout is still useful only for connect/network failure, not normal model latency.

## Durable Result / Friday Closed Follow-Up

CEO raised the edge case where a Sync Delegation job crosses the 60 second hard timeout, or Friday is closed while Hermes is still working. The plan now clarifies:

- `HERMES_SYNC_HARD_TIMEOUT_SECONDS=60` is only Friday's foreground wait limit.
- It must not cancel or discard Hermes work.
- Hermes should keep processing and persist the eventual result to mailbox/results or the agreed async result store.
- Every request needs a durable `correlation_id`.
- Friday should keep an ignored local `pending_hermes_jobs` registry with metadata only.
- On startup, Friday should reconcile pending Hermes jobs and announce completed results at a safe idle moment.
- If Hermes cannot keep processing after direct client disconnect, it must enqueue the job to mailbox before closing the direct path.

## Additional Reliability Policies

CEO asked whether 5 extra concerns are necessary. Decision: all 5 are accepted into the plan, with scoped MVP treatment.

Added to `docs/FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`:

- Tool Intent Validation & Retry Policy
  - Hermes `tool_intent` is untrusted.
  - Friday validates schema/tool/args/allowlist.
  - Friday sends structured `schema_error` back to Hermes.
  - `MAX_TOOL_INTENT_RETRIES=2`.
  - retry exhaustion cancels safely with a spoken explanation.
- Result Read Interrupt
  - full barge-in is not MVP.
  - MVP supports stopping long async result readouts with words like "หยุด", "พอ", "เดี๋ยวก่อน".
  - Friday stores read position by `correlation_id`.
- Graceful Degradation & Fallback UX
  - Hermes/Ollama/mailbox failures must not produce silence or spoken stack traces.
  - Friday speaks a short fallback message and returns to stable mode when possible.
- Context Pruning Strategy
  - prune by priority, not raw FIFO.
  - never prune system/safety/current user/pending confirm/core state.
  - prune stale chat, repeated status events, and verbose saved tool output first.
- Telemetry & Environment Secrets
  - config/secrets come from environment/local ignored config, not hard-code.
  - telemetry includes Hermes TTFB, total latency, fallback reason, retry count, keepalive count, detach/timeout flags.

## Hermes API Docs Follow-Up

CEO supplied Hermes-generated API docs for Friday:

- `D:\AI-Workspace\runtime\hermes-native\workspace\hermes-dashboard-api-for-friday.md`
- `D:\AI-Workspace\runtime\hermes-native\hermes-native-vault\03_Technical_References\hermes-dashboard-api-probe.md`
- `D:\AI-Workspace\agents\hermes\handoff\2026-07-27-phase0-probe.md`

Live probe on 2026-07-27 confirmed:

- Dashboard `http://127.0.0.1:9119` is running now.
- Dashboard HTML returns a session token.
- OpenAPI version is `0.19.0` with 248 paths.
- `/api/health` and `/api/status` work.
- Static docs mention `POST /api/chat`, but live OpenAPI did not list `/api/chat`.
- Known chat candidate is the WebSocket path used by `ask-hermes-pc.mjs`: `/api/ws`, `session.create`, then `prompt.submit`.
- Static docs mention `/api/kanban/...`, but live OpenAPI shows `/api/plugins/kanban/...`.

Action for Phase 0:

- Build Friday's Hermes endpoint manifest from live OpenAPI, not only static docs.
- Probe chat through WebSocket before implementing Sync Delegation.
- Treat dashboard token as ephemeral and never hard-code it.

## Recommended Next Step

Start with Phase 0 + Phase 1 only:

- Phase 0: contract + live Hermes capability probe.
- Phase 1: shadow mode where Friday still answers normally but sends text to Hermes for routing analysis.

Do not jump straight to Hermes-driven tool execution. First prove latency, reliability, and routing quality without changing user-facing Friday behavior.

## Current Repo Hygiene

Observed but not touched:

- `tts_output/` is still untracked runtime output.
- `docs/VOICE_LATENCY_ROADMAP_2026-07-19.md` and `handoff/2026-07-26-jaitts-colab-serious-voice-plan.md` already had pending changes from the JaiTTS planning update.

## Verification

Docs-only planning change. No tests run.
