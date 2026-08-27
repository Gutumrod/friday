# Friday Project Context — Current State

**Last Updated:** 2026-08-27  
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

## Architecture Decision — Home Assistant

As of 2026-08-27, Home Assistant is the selected household smart-home control plane for Friday.

This is now a locked direction, not merely an optional integration idea.

Target relationship:

```text
Friday / Hermes
 -> logical device intent
 -> Friday policy + Confirm Gate
 -> Home Assistant
 -> device/entity integration
      -> LG webOS TV
      -> future IR blaster / legacy AC
      -> future lights, fans, sensors, scenes
```

Direct LG webOS control remains useful as a compatibility/rollback path while Home Assistant parity is being proven. Long term, Friday should reason over logical devices and HA entities instead of raw IP/MAC/vendor details.

IR remains planned, but Home Assistant adoption does not wait for IR hardware.

## Active Branch Stack

### Voice / STT track

| Branch | State | Remaining gate |
|---|---|---|
| `feat/phase0-security-cleanup` | Code prepared; live gate in progress | finish Windows regression + TV security/live validation |
| `feat/phase1-stt-provider-abstraction` | Code prepared | runtime regression on target machine |
| `feat/phase2-stt-benchmark-harness` | Harness prepared | record and run real owner speech dataset |
| `feat/phase3-streaming-stt-contract` | Contract prepared | blocked from production integration until Phase 2 evidence |

### Smart-home / Home Assistant track

| Branch | State | Remaining gate |
|---|---|---|
| `feat/phase4-home-assistant-foundation` | Architecture locked; read-only client/tools prepared | install/connect real HA and verify entities |
| `feat/phase5-home-device-registry` | Registry/aliases prepared | map and verify real entity IDs/capabilities |
| `feat/phase6-smart-home-confirm-gated-tools` | Write tools prepared | Phase 4/5 live gates + confirmation UX validation |
| `feat/phase7-ir-legacy-ac-readiness` | Readiness/runbook prepared | IR hardware purchase + one-AC pilot |
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

## Current Live TV Findings

The current LG TV direct webOS path was rechecked from the target Windows PC.

Verified:

- TV rediscovered on the LAN at `192.168.1.128`
- MAC matched the known paired TV
- webOS ports 3000/3001 were reachable at the rediscovered address
- paired client key still worked
- read-only webOS connection succeeded
- application list returned successfully
- foreground app state could be read; YouTube was observed as `youtube.leanback.v4`
- volume/mute/output state could be read

The prior configured TV IP had become stale because DHCP changed the address. This is evidence for reducing direct raw-IP dependency.

Transition plan:

1. use a DHCP reservation for the TV while direct webOS remains active
2. add LG TV to Home Assistant
3. expose the TV as a stable logical/media entity
4. move Friday device intent behind the HA registry
5. retain direct webOS only as rollback/compatibility until parity is proven

## Media Awareness Direction

Friday should eventually answer useful TV/media state questions without guessing.

Authority order:

```text
1. live Home Assistant/media_player metadata
2. direct webOS read-only metadata while compatibility path exists
3. Friday media-session memory for media Friday launched itself
4. unknown
```

Current direct webOS evidence shows that Friday can know the foreground app and volume, but exact YouTube video title is not exposed by the tested foreground-app response.

Therefore:

- if HA exposes exact media metadata, treat it as authoritative live state
- if Friday itself launches a video/song, store the requested/resolved media as last-known commanded state
- if someone changes playback manually and no live metadata exists, Friday must not pretend it knows the exact title

## Important Safety Decisions

### Credentials

A paired LG webOS client key was previously present in public source history. The Phase 0 branch removes machine/device secrets from current source and moves them to environment configuration.

Before TV control is considered safe again on the machine:

- finish Phase 0 regression
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

Home Assistant is the canonical household control plane.

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

Initial real-HA onboarding should prioritize the LG TV because it is already a known working device and provides an immediate comparison between direct webOS and HA-mediated state/control.

## IR / Legacy AC Direction

IR remains in scope and the Phase 7 readiness/runbook stays valid.

No IR hardware purchase has been made yet. This does not block Phase 4–6 Home Assistant work.

When hardware is purchased, the first pilot should be one IR blaster controlling one downstairs AC through Home Assistant. Friday should not store or transmit raw IR codes directly.

Preferred path:

```text
Friday
 -> Home Assistant climate/logical entity
 -> HA IR integration/script/scene
 -> IR blaster
 -> legacy AC
```

If true AC state is unavailable, the state must be treated as assumed/uncertain.

## What Is Blocked Right Now

The code can continue to be prepared remotely, but these gates require the owner's machines or hardware:

1. finish Phase 0 full regression/security fix + TV live validation
2. Phase 1 runtime regression
3. Phase 2 real speech benchmark
4. install/connect real Home Assistant
5. Phase 4 real HA read-only connection and LG TV entity verification
6. Phase 5 real entity/alias mapping
7. Phase 6 real confirmation + command pilot
8. Phase 7 IR hardware pilot after hardware purchase
9. later remote-access and scene live tests

Until those gates run, documents must say **prepared/pending**, not PASS.

## Merge Strategy When Machines Are Online

Recommended sequence:

1. finish Phase 0 security regression and commit/push validated fix
2. open/review/merge Phase 0
3. validate/open/merge Phase 1
4. run Phase 2 real benchmark; merge harness independently from any provider decision
5. only integrate Phase 3 streaming if benchmark supports it
6. install/connect Home Assistant and add LG TV
7. validate Phase 4 read-only HA + media state
8. validate Phase 5 real registry mapping
9. validate Phase 6 write tools and Confirm Gate UX
10. run Phase 7 IR pilot only after hardware exists
11. continue Phase 8–10 after prerequisite gates

Use stacked PRs while branches still depend on one another; retarget/rebase as earlier phases merge.

## Current Documents

Authoritative reading order:

1. latest dated file under `handoff/`
2. this file — `docs/PROJECT_CONTEXT.md`
3. `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`
4. `docs/PRD.md`
5. phase evidence/contract files on the relevant feature branch

Historical July plans and audits remain useful evidence but may describe superseded architecture. Verify them against current code before acting.
