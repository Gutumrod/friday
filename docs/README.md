# Friday Documentation Index

**Last Updated:** 2026-08-26

Friday has accumulated historical design notes, audits, handoffs, and current plans. Not every document describes the current implementation.

## Read These First

1. latest dated file in `handoff/`
2. `PROJECT_CONTEXT.md` — current repo/branch/gate status
3. `FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md` — active Phase 0–10 roadmap and branch graph
4. `PRD.md` — current product architecture and safety boundaries
5. `WALKTHROUGH.md` — how to run/test the stable baseline on `master`

## Current Architecture Summary

```text
Voice input
 -> STT
 -> Friday runtime
 -> LLM/Hermes reasoning
 -> structured tool intent
 -> Friday validation / Confirm Gate
 -> approved executor
 -> result
 -> Friday voice output
```

Current stable `master` uses native structured function calling. Documents that describe `[TOOL: ...]` text parsing are historical.

Current normal TTS path is JaiTTS local with Edge TTS fallback/alternate voice. Documents that describe Edge TTS as the only or primary current voice are historical.

Current production STT remains Google Cloud STT with fallback behavior. Typhoon and streaming STT are prepared/evaluated on feature branches and are not yet the merged production default.

## Current Development Branches

- `feat/phase0-security-cleanup`
- `feat/phase1-stt-provider-abstraction`
- `feat/phase2-stt-benchmark-harness`
- `feat/phase3-streaming-stt-contract`
- `feat/phase4-home-assistant-foundation`
- `feat/phase5-home-device-registry`
- `feat/phase6-smart-home-confirm-gated-tools`
- `feat/phase7-ir-legacy-ac-readiness`
- `feat/phase8-hermes-home-tool-intent-contract`
- `feat/phase9-remote-command-security-contract`
- `feat/phase10-home-scene-orchestration`

See `PROJECT_CONTEXT.md` for readiness/gates and branch dependencies.

## Historical Documents

Dated documents from July 2026 remain useful for:

- why a bug was fixed a particular way
- latency experiments
- TV/camera live evidence
- Hermes evolution
- audit history
- rollback/history context

They are not automatically current requirements.

Examples of historical/reference docs include:

- `LIVE_UPGRADE_PLAN_2026-07-03.md`
- `LIVE_MIGRATION_READINESS_2026-07-03.md`
- `LATENCY_PHASE1_2026-07-02.md`
- `VOICE_LATENCY_ROADMAP_2026-07-19.md`
- `FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`
- `FRIDAY_DEVELOPMENT_PLAN_2026-07-28.md`

When a historical document conflicts with the latest handoff/current context/current code, use the newer source.

## Evidence Rule

Do not convert “code prepared” into “PASS” without executing the required gate.

Examples requiring real environment evidence:

- microphone/STT latency and accuracy
- Windows regression
- TV re-pair/live behavior
- Home Assistant connectivity/entity mapping
- Home Assistant write behavior
- IR blaster/AC behavior
- remote-access security
- scene/automation execution

## Safety Rule

All real-world side effects remain subject to Friday's execution policy and Confirm Gate. Hermes, remote clients, UI, and Home Assistant integrations do not get a bypass simply because they use a different transport.
