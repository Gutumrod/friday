# Friday Project Context — Current State

**Last Updated:** 2026-08-26  
**Repository:** `Gutumrod/friday`  
**Primary branch:** `master`  
**Current strategy:** keep `master` stable; prepare work on phase branches, then validate/open PRs/merge when owner machines and hardware are available.

## Current Status

Friday is no longer in the July 2026 “build a tool parser” stage.

Current verified baseline on `master` already has:

- Windows turn-based voice runtime
- Google Cloud STT (`th-TH`) with `recognize_google()` fallback on Cloud request failure
- Ollama native structured function calling
- `TOOLS` + `TOOL_SCHEMAS`
- `CONFIRM_GATED` safety boundary
- local computer tools
- timers/alarms
- camera tools
- LG webOS TV tools
- vault memory/history
- JaiTTS as the normal local TTS path, with Edge TTS fallback/explicit alternate voice
- FastAPI backend and UI event stream
- Hermes dispatch/notification plus shadow-mode foundation

The old `[TOOL: ...]` parser design is obsolete.

## Target Architecture

```text
Mic
 -> STT provider
 -> Friday runtime
 -> LLM / Hermes reasoning
 -> structured intent
 -> Friday schema/policy validation
 -> Confirm Gate when side-effecting
 -> executor
      -> local PC tools
      -> Home Assistant
      -> other approved integrations
 -> result
 -> TTS
```

Friday remains the safety gateway and executor. Hermes must not bypass Friday to control physical devices.

## Active Branch Stack

### Voice / STT track

| Branch | State | Remaining gate |
|---|---|---|
| `feat/phase0-security-cleanup` | Code prepared | Windows regression + TV re-pair/live validation |
| `feat/phase1-stt-provider-abstraction` | Code prepared | runtime regression on target machine |
| `feat/phase2-stt-benchmark-harness` | Harness prepared | record and run real owner speech dataset |
| `feat/phase3-streaming-stt-contract` | Contract prepared | blocked from production integration until Phase 2 evidence |

### Smart-home / Home Assistant track

| Branch | State | Remaining gate |
|---|---|---|
| `feat/phase4-home-assistant-foundation` | Read-only client/tools prepared | connect to real Home Assistant and verify entities |
| `feat/phase5-home-device-registry` | Registry/aliases prepared | map and verify real entity IDs/capabilities |
| `feat/phase6-smart-home-confirm-gated-tools` | Write tools prepared | Phase 4/5 live gates + confirmation UX validation |
| `feat/phase7-ir-legacy-ac-readiness` | Readiness/runbook prepared | IR hardware + one-AC pilot |
| `feat/phase8-hermes-home-tool-intent-contract` | Validator contract prepared | Hermes live tool-intent remains disabled |
| `feat/phase9-remote-command-security-contract` | Security policy/contract prepared | secure remote transport/auth design and live verification |
| `feat/phase10-home-scene-orchestration` | Scene orchestration prepared | real Home Assistant scenes + live gate |

## Branch Dependency Graph

```text
master
  -> phase0
      -> phase1
          -> phase2
              -> phase3
          -> phase4
              -> phase5
                  -> phase6
                      -> phase7
                          -> phase8
                              -> phase9
                                  -> phase10
```

Phase 3 streaming STT does not block Home Assistant development. Both tracks share the security/STT abstraction baseline but can be reviewed independently where dependencies permit.

## Important Safety Decisions

### Credentials

A paired LG webOS client key was previously present in public source history. The Phase 0 branch removes machine/device secrets from current source and moves them to environment configuration.

Before TV control is considered safe again on the machine:

- pull the Phase 0 branch
- create local `.env`
- re-pair/rotate the LG client key
- never commit the new key

Future Home Assistant tokens follow the same rule.

### Physical device commands

A successful Home Assistant service response does not prove that a physical device actually changed state.

Friday should say that it **sent the command** unless state was independently verified.

This is especially important for IR devices because IR is usually one-way and the physical remote can change state without Home Assistant knowing.

### Confirm Gate

All current planned smart-home write tools remain confirm-gated. Phase 8 Hermes intent validation cannot override this policy.

## STT Direction

Current production default remains Google Cloud STT.

The prepared branch stack introduces a provider boundary and a benchmark harness so Google vs Typhoon is selected from real evidence rather than vendor benchmark claims.

The benchmark must prioritize:

- command-critical accuracy
- Thai-English code switching
- numbers/temperature/device names
- median/p95 latency
- stability and target-machine resource usage

Streaming integration is blocked until the benchmark justifies it.

## Home Assistant Direction

Home Assistant is the intended household control plane.

Friday should operate on logical names such as:

```text
downstairs_ac
living_room_tv
bedroom_fan
```

with Thai aliases such as:

```text
แอร์ล่าง
ทีวีห้องนั่งเล่น
พัดลมห้องนอน
```

The registry maps these logical devices to Home Assistant entities and validates allowed capabilities. Friday/Hermes should not reason over raw IP/MAC/vendor details.

Persistent automation belongs in Home Assistant whenever practical so it continues working even if Friday, Hermes, or the LLM is offline.

## What Is Blocked Right Now

The code can continue to be prepared remotely, but these gates require the owner's machines or hardware:

1. Phase 0 full regression and TV live validation
2. Phase 1 runtime regression
3. Phase 2 real speech benchmark
4. Phase 4 real Home Assistant connection
5. Phase 5 real entity/alias mapping
6. Phase 6 real confirmation + command pilot
7. Phase 7 IR hardware pilot
8. later remote-access and scene live tests

Until those gates run, documents must say **prepared/pending**, not PASS.

## Merge Strategy When Machines Are Online

Recommended sequence:

1. sync local repo with `master`
2. run Phase 0 security tests/regression and re-pair TV
3. open/review/merge Phase 0
4. validate/open/merge Phase 1
5. run Phase 2 real benchmark; merge harness independently from any provider decision
6. only integrate Phase 3 streaming if benchmark supports it
7. validate Phase 4 read-only Home Assistant
8. validate Phase 5 real registry mapping
9. validate Phase 6 write tools and Confirm Gate UX
10. continue Phase 7–10 only after prerequisite gates

Use stacked PRs while branches still depend on one another; retarget/rebase as earlier phases merge.

## Current Documents

Authoritative reading order:

1. latest dated file under `handoff/`
2. this file — `docs/PROJECT_CONTEXT.md`
3. `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`
4. `docs/PRD.md`
5. phase evidence/contract files on the relevant feature branch

Historical July plans and audits remain useful evidence but may describe superseded architecture. Verify them against current code before acting.
