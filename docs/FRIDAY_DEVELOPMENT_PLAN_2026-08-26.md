# Friday Development Plan — Current Roadmap

**Date:** 2026-08-26  
**Repository:** `Gutumrod/friday`  
**Stable branch:** `master`  
**Development model:** phase branches are prepared first; PR/merge waits for required local/hardware evidence.

## Goal

Build Friday into the conversational and safety front door for local computer tools, Hermes, and Home Assistant without letting reasoning components bypass execution policy.

Long-term control flow:

```text
Mic
 -> STT
 -> Friday runtime
 -> LLM / Hermes reasoning
 -> validated structured intent
 -> Friday Confirm Gate / policy
 -> local executor or Home Assistant
 -> result / state evidence
 -> Friday TTS
```

## Current Baseline on `master`

- turn-based Windows voice runtime
- Google Cloud STT (`th-TH`) + free Google fallback on Cloud request failure
- native Ollama structured tool calling
- `TOOLS` / `TOOL_SCHEMAS`
- `CONFIRM_GATED`
- local system tools, timers, alarms
- camera and LG webOS TV tools
- JaiTTS local voice primary, Edge TTS fallback/alternate voice
- memory/history vault
- FastAPI + UI service boundary
- Hermes dispatch/notification/shadow foundation

`master` intentionally does **not** yet contain the new Phase 0–10 implementation stack.

## Branch Graph

```text
master
  -> feat/phase0-security-cleanup
      -> feat/phase1-stt-provider-abstraction
          -> feat/phase2-stt-benchmark-harness
              -> feat/phase3-streaming-stt-contract
          -> feat/phase4-home-assistant-foundation
              -> feat/phase5-home-device-registry
                  -> feat/phase6-smart-home-confirm-gated-tools
                      -> feat/phase7-ir-legacy-ac-readiness
                          -> feat/phase8-hermes-home-tool-intent-contract
                              -> feat/phase9-remote-command-security-contract
                                  -> feat/phase10-home-scene-orchestration
```

The Phase 3 streaming-STT line is evidence-gated and does not block the Home Assistant line.

## Phase Status

### Phase 0 — Security / Machine Config

**Branch:** `feat/phase0-security-cleanup`  
**State:** CODE PREPARED — LIVE GATE PENDING

Prepared:

- move LG webOS paired key and machine-specific TV values out of source
- machine-local `.env` configuration
- safe startup diagnostics without printing secret values
- fail-closed TV tool behavior when config is incomplete
- phase-specific security regression coverage

Required before merge:

- run tests on target Windows environment
- rotate/re-pair the LG TV client key because the old key existed in public history
- run existing TV regressions
- live TV verification

### Phase 1 — STT Provider Abstraction

**Branch:** `feat/phase1-stt-provider-abstraction`  
**State:** CODE PREPARED — RUNTIME GATE PENDING

Prepared:

- STT provider contract/result/error model
- Google provider preserving current behavior
- optional Typhoon adapter path
- provider selection via environment configuration
- default remains Google until evidence says otherwise

Do not force Typhoon into Windows production merely because the adapter exists.

### Phase 2 — Google vs Typhoon Benchmark

**Branch:** `feat/phase2-stt-benchmark-harness`  
**State:** HARNESS PREPARED — DATASET PENDING

Prepared benchmark measures:

- transcription correctness / CER
- command-critical accuracy
- Thai-English code switching
- numbers / temperature / device names
- median and p95 latency
- provider failures

Required evidence: real owner speech recorded under normal operating conditions.

### Phase 3 — Streaming STT

**Branch:** `feat/phase3-streaming-stt-contract`  
**State:** CONTRACT PREPARED — PRODUCTION INTEGRATION BLOCKED BY PHASE 2

Prepared only as an interface/state-machine boundary so future streaming ASR can expose partial/final transcripts cleanly.

Do not replace the stable turn-based microphone loop until the benchmark supports the decision and barge-in/TTS feedback behavior is tested.

### Phase 4 — Home Assistant Read-Only Foundation

**Branch:** `feat/phase4-home-assistant-foundation`  
**State:** CODE PREPARED — REAL HA GATE PENDING

Prepared:

- authenticated Home Assistant client
- token hidden from object representation/errors
- health/state/list read operations
- optional registration: HA tools are absent when HA config is unavailable
- no physical-device write service in this phase

Required before merge: connect to real Home Assistant and verify known entities.

### Phase 5 — Logical Home Device Registry

**Branch:** `feat/phase5-home-device-registry`  
**State:** CODE PREPARED — REAL ENTITY MAPPING PENDING

Purpose:

- logical device IDs instead of raw entity IDs
- Thai aliases
- capability allowlists
- duplicate alias detection
- unknown/ambiguous devices fail closed

Example:

```text
downstairs_ac -> climate.downstairs_ac
aliases: แอร์ล่าง, แอร์ชั้นล่าง
capabilities: power, temperature, mode, fan
```

### Phase 6 — Confirm-Gated Smart-Home Writes

**Branch:** `feat/phase6-smart-home-confirm-gated-tools`  
**State:** CODE PREPARED — MERGE BLOCKED BY PHASE 4/5 LIVE GATES

Prepared write intents include:

- logical device power
- AC temperature
- HVAC mode
- fan mode

Safety rules:

- model uses logical device alias, not arbitrary raw entity ID
- capability/range validation happens before service call
- all write tools register into `CONFIRM_GATED`
- unknown/malformed/out-of-range requests do not call Home Assistant
- a successful HA service call means “command sent”, not guaranteed physical-state confirmation

### Phase 7 — Legacy AC / IR Readiness

**Branch:** `feat/phase7-ir-legacy-ac-readiness`  
**State:** READINESS/RUNBOOK — HARDWARE PENDING

First pilot should be one IR blaster + one downstairs AC.

Prefer exposing the AC through a Home Assistant climate abstraction. If the integration cannot know true device state, mark state as assumed/uncertain.

### Phase 8 — Hermes Home Tool Intent Contract

**Branch:** `feat/phase8-hermes-home-tool-intent-contract`  
**State:** VALIDATOR PREPARED — LIVE EXECUTION DISABLED

Hermes may propose a structured tool-intent envelope, but Friday validates tool allowlist/schema/policy. Write intent is rejected if Friday does not have the corresponding Confirm Gate.

Hermes cannot request `requires_confirmation=false` or otherwise override Friday safety policy.

### Phase 9 — Remote Command Security

**Branch:** `feat/phase9-remote-command-security-contract`  
**State:** POLICY/CONTRACT PREPARED — NO PUBLIC EXPOSURE ENABLED

Remote use requires:

- authenticated secure transport
- explicit authorization
- audit trail
- replay/duplicate protection where implemented
- stronger confirmation policy for remote side effects where appropriate

Do not expose Friday or Home Assistant unauthenticated to the public internet.

### Phase 10 — Home Scene Orchestration

**Branch:** `feat/phase10-home-scene-orchestration`  
**State:** PREPARED — REAL SCENE/LIVE GATE PENDING

Friday may activate allowlisted logical scenes such as:

- arriving home
- bedtime
- away mode

Scene activation remains a side effect and must be confirm-gated.

Persistent triggers, schedules, and household automation logic should live in Home Assistant whenever practical so the home continues working even if Friday/Hermes/LLM is offline.

## Engineering Rules

1. inspect current code and latest handoff before editing
2. keep secrets and device credentials out of source
3. preserve rollback paths
4. never claim a gate passed without executing the required test/evidence
5. side effects require confirmation unless explicitly approved otherwise
6. unknown tool/device/entity/capability fails closed
7. Hermes cannot bypass Friday execution policy
8. semantic commands must not be coupled to vendor hardware
9. real-device phases need real-device evidence
10. commit/push checkpoints so work remains portable across machines

## Required Local Validation Sequence

When the owner machine is online:

1. Phase 0 security + full regression + TV re-pair/live test
2. Phase 1 STT runtime regression
3. Phase 2 real speech benchmark
4. Phase 3 only if benchmark supports streaming adoption
5. Phase 4 real Home Assistant read-only test
6. Phase 5 real alias/entity verification
7. Phase 6 confirmation/write pilot on a low-risk device
8. Phase 7 one-AC IR pilot
9. Phase 8 Hermes intent tests before any live execute path
10. Phase 9 remote-security validation before remote side effects
11. Phase 10 scene pilot

## PR / Merge Strategy

Do not open one giant PR for all phases.

Use stacked PRs following branch dependencies. Merge validated prerequisites first, then retarget/rebase dependent PRs as needed.

A branch being “code prepared” is not the same as “ready to merge.” Hardware/runtime gates remain authoritative.
