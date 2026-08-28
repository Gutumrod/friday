# Friday Development Plan — Current Roadmap

**Date:** 2026-08-27  
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

## Architecture Decision — Home Assistant Is Locked In

As of 2026-08-27, Home Assistant is no longer just an optional future integration. It is the selected smart-home control plane for Friday.

Target ownership:

```text
Friday / Hermes
 -> logical intent + safety policy
 -> Home Assistant
 -> device integration
      -> LG webOS TV
      -> IR blaster / legacy AC
      -> future lights, fans, sensors, scenes
```

Rules:

- Friday remains the conversational safety gateway.
- Home Assistant owns household device/entity integration and persistent automation where practical.
- Friday/Hermes should not depend on raw IP/MAC/vendor details in the intent layer.
- Direct LG webOS support may remain as a compatibility/rollback path during migration.
- Home Assistant adoption must not wait for IR hardware.
- IR blaster work remains hardware-dependent and can start later when hardware is purchased.

Media-awareness direction:

- HA should expose the LG TV as a `media_player` entity where available.
- Friday should be able to read TV on/off state, active source/app, volume, and other media state exposed by HA.
- Friday should maintain a small media-session record when Friday itself launches YouTube/media so it remembers what it asked the TV to play.
- If the TV/HA integration does not expose the exact YouTube title currently playing, Friday must treat its own remembered title as last-known state, not authoritative live metadata.

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
**State:** CODE PREPARED — LIVE GATE IN PROGRESS

Prepared:

- move LG webOS paired key and machine-specific TV values out of source
- machine-local `.env` configuration
- safe startup diagnostics without printing secret values
- fail-closed TV tool behavior when config is incomplete
- phase-specific security regression coverage

Current live findings:

- Phase 0 security checks passed 5/5 on the target Windows PC.
- Full Friday self-check reached 78/80; one unrelated JaiTTS/Hugging Face runtime failure remains and one Hermes redaction defect was found and fixed locally for retest/commit.
- LG TV direct webOS pairing still works with the existing paired key.
- The TV was rediscovered at `192.168.1.128`; its MAC matched the known TV and read-only webOS connection succeeded.
- The IP had changed through DHCP, confirming that raw IP dependence should be reduced and/or protected with DHCP reservation during transition to Home Assistant.

Required before merge:

- finish regression after the redaction fix
- commit/push validated Phase 0 fix
- rotate/re-pair the LG TV client key because the old key existed in public history
- finish live TV regression
- configure DHCP reservation when router admin access is available, or move TV addressing behind Home Assistant once Phase 4 is active

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

### Phase 4 — Home Assistant Foundation

**Branch:** `feat/phase4-home-assistant-foundation`  
**State:** ARCHITECTURE DECISION LOCKED — CODE PREPARED — REAL HA GATE PENDING

Home Assistant is now the selected smart-home control plane.

Prepared:

- authenticated Home Assistant client
- token hidden from object representation/errors
- health/state/list read operations
- optional registration: HA tools are absent when HA config is unavailable
- no physical-device write service in this phase

Real-HA onboarding target:

1. bring up Home Assistant on the home network
2. add the LG webOS TV integration
3. verify the LG TV appears as a stable media/device entity
4. verify read-only state from Friday through HA
5. map the TV into the logical device registry
6. keep direct webOS tools available as rollback until HA parity is proven

Media-state acceptance should include, where exposed by HA:

- powered/available state
- active app/source
- volume/mute/output
- media title/content metadata when the integration actually supplies it

Do not claim exact YouTube playback title unless live metadata proves it or clearly label Friday's own launch record as last-known state.

Required before merge: connect to a real Home Assistant instance and verify known entities.

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
living_room_tv -> media_player.living_room_tv
downstairs_ac -> climate.downstairs_ac
aliases: ทีวีห้องนั่งเล่น, แอร์ล่าง, แอร์ชั้นล่าง
capabilities: status, media, power, temperature, mode, fan
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
**State:** READINESS/RUNBOOK PREPARED — HARDWARE PURCHASE PENDING

IR remains in scope, but it does not block Home Assistant adoption.

When hardware is purchased, first pilot should be:

- one Broadlink-compatible IR blaster or other HA-supported IR device
- one downstairs legacy AC
- one room only
- verify power + temperature + mode behavior

Preferred architecture:

```text
Friday
 -> Home Assistant climate/logical entity
 -> HA IR integration / script / scene
 -> IR blaster
 -> legacy AC
```

Friday must not store or send raw IR codes directly.

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

## Post-Phase-10 Media Awareness Extension

No implementation branch is created yet. This is a planned extension after the Home Assistant media path is proven.

Goal: Friday should answer useful questions such as:

- “ทีวีเปิดอะไรอยู่”
- “ตอนนี้เปิด YouTube อยู่ไหม”
- “เสียงทีวีเท่าไหร่”
- “เมื่อกี้เปิดเพลงอะไรให้กู”

State sources should be ranked by authority:

```text
1. live Home Assistant/media_player metadata
2. direct webOS read-only metadata while compatibility path exists
3. Friday media-session memory for media Friday launched itself
4. unknown — never guess
```

This extension must clearly distinguish authoritative current state from last-known commanded state.

## Integration Development Workflow — Explore, Record, Productize

For new household devices and integrations, Friday does **not** need to support the device before real-world testing begins. During development, ChatGPT connected to the home PC may be used as an exploration/test bench to discover and verify a working control path first.

Canonical workflow:

```text
Owner request
 -> ChatGPT + connected home PC explores the real device
 -> identify working protocol/API/tool path
 -> record command, inputs, response, failure cases, auth and safety behavior
 -> repeat to verify deterministic behavior
 -> normalize vendor-specific operations into logical capabilities
 -> implement the verified path as a Friday tool/adapter
 -> add schema validation + Confirm Gate for side effects
 -> add regression/live evidence
```

Rules for this workflow:

- Exploration may use temporary scripts, shell commands, browser/admin UI, discovery scans, or remote-PC tooling.
- Exploration methods are evidence, not automatically production architecture.
- Production Friday should prefer deterministic interfaces such as Home Assistant APIs, local HTTP/WebSocket APIs, MQTT, or documented LAN protocols.
- Do not productize brittle browser-click automation as the normal control path when a stable API/protocol exists.
- Never copy temporary credentials, session cookies, tokens, device keys, IP-specific secrets, or raw IR codes into source.
- Every successful device experiment should leave a compact integration record before implementation.

Minimum integration record:

```text
Device / logical ID
Connection protocol and discovery method
Read capabilities
Write capabilities
Authentication / secret storage
Representative request and response shape
Failure / offline behavior
Confirmation policy
Known limitations and state confidence
Production path selected for Friday
```

The LG TV experiment on 2026-08-27 is the reference example: direct webOS discovery/control was proven first, DHCP/IP instability was observed, read-only media state was tested, and those findings now inform the Home Assistant migration and Friday tool design.

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
11. Home Assistant is the canonical household control plane; vendor-specific direct integrations are compatibility layers unless explicitly retained
12. use ChatGPT + connected PC as an exploration bench when useful, but productize only verified deterministic control paths into Friday

## Required Local Validation Sequence

When the owner machine is online:

1. finish Phase 0 security regression + TV direct-path validation
2. Phase 1 STT runtime regression
3. Phase 2 real speech benchmark
4. Phase 3 only if benchmark supports streaming adoption
5. install/connect real Home Assistant and add LG webOS TV
6. Phase 4 read-only HA test including TV media state where exposed
7. Phase 5 real alias/entity verification
8. Phase 6 confirmation/write pilot on a low-risk device
9. Phase 7 one-AC IR pilot only after hardware is purchased
10. Phase 8 Hermes intent tests before any live execute path
11. Phase 9 remote-security validation before remote side effects
12. Phase 10 scene pilot
13. media-awareness extension after the HA TV/media path is stable

## PR / Merge Strategy

Do not open one giant PR for all phases.

Use stacked PRs following branch dependencies. Merge validated prerequisites first, then retarget/rebase dependent PRs as needed.

A branch being “code prepared” is not the same as “ready to merge.” Hardware/runtime gates remain authoritative.
