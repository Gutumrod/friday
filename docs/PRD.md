# PRD — Friday AI Assistant

**Repository:** `Gutumrod/friday`  
**Primary branch:** `master`  
**Last Updated:** 2026-08-26  
**Status:** Active development; implementation is staged on feature branches and not yet merged to `master`

## 1. Product Objective

Friday is a Thai-first voice assistant that acts as the conversational front door for the owner's computer, agents, and smart-home environment.

The long-term product is not a single LLM script. Friday is the safety and execution boundary between natural-language requests and real-world actions.

Target architecture:

```text
Mic
 -> STT
 -> Friday conversation/runtime
 -> LLM and/or Hermes reasoning
 -> structured tool intent
 -> Friday validation + Confirm Gate
 -> local tool / Home Assistant / other approved executor
 -> result
 -> Friday TTS
```

Core principles:

- Friday owns execution of real-world side effects.
- Hermes may reason, plan, or propose tool intent, but cannot bypass Friday validation.
- Every side-effect tool is confirm-gated unless a future explicit policy says otherwise.
- Home Assistant is the planned smart-home control plane; Friday should not encode vendor-specific IR/device behavior in its semantic command layer.
- Secrets, paired keys, tokens, and machine-specific values must not be committed to source.
- STT/TTS/providers must remain replaceable where practical.

## 2. Current Production Baseline on `master`

The current runtime is Windows-oriented and remains turn-based.

```text
Microphone
 -> SpeechRecognition capture
 -> Google Cloud STT (`th-TH`)
 -> `recognize_google()` fallback on Cloud request failure
 -> Ollama native structured function calling
 -> Friday `TOOLS` / `TOOL_SCHEMAS`
 -> `CONFIRM_GATED` for side effects
 -> tool execution
 -> JaiTTS local voice primary
 -> Edge TTS fallback / explicit alternate voice
 -> pygame playback
```

Current major capabilities include:

- Thai voice conversation
- structured native tool calling
- local computer tools
- timers/alarms
- memory/history vault
- camera snapshot tools
- LG webOS TV control
- confirm-gated side effects
- Hermes dispatch/notification and shadow-mode foundation
- FastAPI service boundary and UI event stream

Important: older documentation that describes `[TOOL: ...]` text parsing, Edge-TTS as the primary voice, or Faster-Whisper as the current plan is historical and not authoritative.

## 3. Product Boundaries

### Friday responsibilities

- voice input/output orchestration
- conversation state
- structured tool exposure
- schema/argument validation
- confirmation and safety policy
- local execution boundary
- audit/latency evidence
- dispatch to Hermes where appropriate
- smart-home semantic commands through Home Assistant

### Hermes responsibilities

- deeper reasoning and worker routing
- asynchronous/complex work coordination where explicitly enabled
- proposing validated tool intent in later phases

Hermes does not receive raw Home Assistant credentials and must not execute home-device actions directly.

### Home Assistant responsibilities

- device/vendor integrations
- entity state
- smart-home service execution
- persistent household automations/scenes
- IR/device abstraction where possible

Friday should communicate desired semantic state rather than raw IR codes, MAC addresses, or vendor commands.

## 4. Current Development Tracks

Implementation is intentionally split into branches so work can be prepared while the owner machines are offline.

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

The STT streaming track and Home Assistant track can be reviewed independently after their shared prerequisites.

## 5. Phase Goals

| Phase | Goal | Current state |
|---|---|---|
| 0 | Remove committed machine/device credentials and fail closed | Code prepared; live Windows/TV gate pending |
| 1 | Replaceable STT provider abstraction | Code prepared; runtime regression pending |
| 2 | Real-owner Google vs Typhoon benchmark harness | Harness prepared; real audio dataset pending |
| 3 | Streaming STT contract/state model | Contract prepared; production integration blocked by Phase 2 evidence |
| 4 | Home Assistant authenticated read-only foundation | Code prepared; real HA gate pending |
| 5 | Logical home-device registry and Thai aliases | Code prepared; real entity mapping pending |
| 6 | Confirm-gated Home Assistant write tools | Code prepared; merge blocked by Phase 4/5 live gates |
| 7 | Legacy AC / IR readiness | Runbook/readiness only; hardware pending |
| 8 | Hermes home tool-intent validation contract | Validator prepared; no live execute path |
| 9 | Remote command security contract | Policy/contract only; no public exposure enabled |
| 10 | Home scene orchestration | Prepared on feature branch; must remain confirm-gated and HA-owned |

## 6. Safety Requirements

1. All side effects use `CONFIRM_GATED` unless explicitly approved otherwise.
2. Unknown devices/tools/aliases fail closed; never guess.
3. Credentials never appear in source, logs, history, prompts, or Hermes payloads.
4. Remote access must require authenticated secure transport; do not expose unauthenticated Home Assistant/Friday endpoints to the public internet.
5. A successful Home Assistant service call means only that the command was accepted; Friday must not claim the physical device definitely changed state unless verified.
6. IR-controlled state may be assumed/uncertain because the original physical remote can change device state outside Friday/Home Assistant awareness.
7. Production changes require regression tests and real-device evidence where hardware behavior is involved.

## 7. Success Criteria

Friday is successful when it can:

- understand normal Thai and Thai-English commands reliably with measured latency
- remain usable when one STT/TTS/cloud dependency degrades
- expose tools through structured schemas rather than text parsing
- prevent unintended side effects through confirmation and allowlists
- delegate complex reasoning without giving Hermes direct execution bypasses
- control supported household devices semantically through Home Assistant
- preserve household automations even when Friday/Hermes/LLM is offline
- provide enough evidence/logging to diagnose latency and execution failures

## 8. Current Source-of-Truth Documents

Read in this order:

1. latest dated file in `handoff/`
2. `docs/PROJECT_CONTEXT.md`
3. `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`
4. this PRD
5. phase-specific evidence/contract documents on their feature branches

Older dated plans remain useful as history, but they do not override the current context or latest handoff.
