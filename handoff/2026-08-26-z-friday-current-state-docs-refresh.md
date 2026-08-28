# Friday Current-State Documentation Refresh Handoff

Date: 2026-08-26
Repository: `Gutumrod/friday`
Branch: `master`

## What Changed

Documentation-only refresh on `master`. No Phase 0–10 implementation was merged into `master` in this documentation pass.

Updated:

- `docs/PRD.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/WALKTHROUGH.md`
- `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`

Added:

- `docs/README.md`
- this handoff

## Why

The July documents still described superseded architecture, including:

- `[TOOL: ...]` embedded-text parsing as future work
- Edge TTS as the primary/current voice
- Faster-Whisper as the planned/current STT direction
- Hermes/tool integration as largely unimplemented

Those claims no longer matched current code or the prepared 2026-08-26 branch stack.

## Current Stable Baseline

`master` remains the stable/pre-Phase-0 implementation baseline plus current documentation.

Verified architecture before the new feature branches:

- Windows turn-based voice runtime
- Google Cloud STT `th-TH` + free Google fallback on Cloud request failure
- Ollama native structured function calling
- `TOOLS`, `TOOL_SCHEMAS`, `CONFIRM_GATED`
- local computer tools, timers, alarms
- camera and LG webOS TV controls
- JaiTTS normal local TTS path with Edge TTS fallback/alternate voice
- vault memory/history
- FastAPI/UI service boundary
- Hermes dispatch/notification/shadow foundation

## Prepared Branch Stack

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

## Branch Readiness Summary

- Phase 0: security/config code prepared; Windows regression + TV key rotation/re-pair/live test pending
- Phase 1: STT provider abstraction prepared; target-machine regression pending
- Phase 2: benchmark harness prepared; real owner audio dataset pending
- Phase 3: streaming STT contract prepared; production integration blocked by Phase 2 evidence
- Phase 4: Home Assistant read-only client/tools prepared; real HA connection pending
- Phase 5: logical device registry/Thai aliases prepared; real entity mapping pending
- Phase 6: confirm-gated HA write tools prepared; merge blocked by Phase 4/5 live gates
- Phase 7: IR/legacy-AC readiness prepared; hardware pilot pending
- Phase 8: Hermes tool-intent validator prepared; no live execute path
- Phase 9: remote security policy/contract prepared; no public remote exposure enabled
- Phase 10: Home Assistant scene orchestration prepared; real scene/live validation pending

## Important Safety State

1. A paired LG webOS client key existed in public source history. Phase 0 removes current-source exposure, but the old key should be considered exposed and must be rotated/re-paired before TV control is trusted again.
2. Home Assistant tokens must remain machine-local and must never be sent to Hermes or committed.
3. Home Assistant accepting a service call is not proof a physical device changed state. Friday should say the command was sent unless independently verified.
4. IR state may be assumed/uncertain because physical remotes can change the device outside Friday/Home Assistant awareness.
5. Smart-home write tools remain confirm-gated.
6. Hermes cannot override Friday confirmation/execution policy.

## Required Work When Owner Machine Is Online

Do not start by merging the newest branch.

Start from Phase 0 and collect evidence in dependency order:

1. pull/fetch repository and branches
2. run Phase 0 tests/full regression
3. create local `.env`
4. rotate/re-pair LG TV key and run live TV verification
5. review/open/merge Phase 0
6. continue Phase 1 and Phase 2 STT validation
7. validate Home Assistant Phase 4/5 before Phase 6 writes
8. use one low-risk device before IR AC
9. keep Hermes live home execution disabled until its dedicated gate

## PR Strategy

Use stacked PRs. Do not combine Phase 0–10 into one large PR.

Merge validated prerequisites first, then retarget/rebase dependent branches.

“Code prepared” does not mean “Gate PASS” or “ready to merge.”

## Current Reading Order

1. `AGENTS.md`
2. this handoff
3. `docs/README.md`
4. `docs/PROJECT_CONTEXT.md`
5. `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`
6. `docs/PRD.md`
7. phase-specific evidence/contract docs on the relevant feature branch

Historical July documents are reference/evidence only where they conflict with current code or these current-state documents.
