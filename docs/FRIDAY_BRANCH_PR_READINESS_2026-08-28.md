# Friday Branch / PR Readiness — 2026-08-28

Repository: `Gutumrod/friday`

Purpose: one authoritative checklist for deciding which prepared branches may be opened as PRs, which may only be draft PRs, and which remain blocked by live/hardware evidence.

## Reconciled branch graph

```text
master
  -> feat/phase0-security-cleanup
      -> feat/phase1-stt-provider-abstraction
          -> feat/phase2-stt-benchmark-harness
              -> feat/phase3-streaming-stt-contract
          -> feat/phase4-home-assistant-foundation
              -> feat/phase5-home-device-registry
                  -> feat/phase6-smart-home-confirm-gated-tools
                      -> feat/phase7-ir-legacy-ac-readiness   # IR lane; does not block Phase 8
                      -> feat/phase8-hermes-home-tool-intent-contract
                          -> feat/phase9-remote-command-security-contract
                              -> feat/phase10-home-scene-orchestration

master
  -> feat/camera-discovery-tool
```

All parent relationships above were reconciled on 2026-08-28. Each listed parent is now an ancestor of its child branch.

## Readiness matrix

| Branch | Non-live evidence | Remaining live/hardware gate | PR status |
|---|---|---|---|
| `feat/camera-discovery-tool` | Camera metadata sanitization PASS; live read-only discovery found Tapo C210; diff-check PASS | No camera write/stream gate in this scope | **READY FOR INDEPENDENT PR** |
| `feat/phase0-security-cleanup` | Phase 0 security 5/5 PASS; Hermes URL/Bearer redaction PASS; full self-check 79/80 with only unrelated JaiTTS/HF failure | Rotate/re-pair historical LG key; final TV + guarded API regression | **DRAFT PR / MERGE BLOCKED** |
| `feat/phase1-stt-provider-abstraction` | Phase-specific checks 7/7 PASS | Runtime/voice parity on target setup | **DRAFT READY** |
| `feat/phase2-stt-benchmark-harness` | Metric/harness checks 6/6 PASS | Real owner-speech dataset + Google/Typhoon benchmark evidence | **DRAFT READY / EVIDENCE BLOCKED** |
| `feat/phase3-streaming-stt-contract` | Contract checks 6/6 PASS | Production adoption blocked by Phase 2 benchmark evidence | **DRAFT ONLY** |
| `feat/phase4-home-assistant-foundation` | HA client/runtime checks 6/6 PASS | Real Home Assistant instance + real entity read-only verification | **DRAFT READY / LIVE HA BLOCKED** |
| `feat/phase5-home-device-registry` | Registry checks 7/7 PASS | Real HA entity/alias mapping | **DRAFT READY / LIVE HA BLOCKED** |
| `feat/phase6-smart-home-confirm-gated-tools` | Confirm-gated write checks 8/8 PASS | Low-risk real HA write pilot after Phases 4/5 | **DRAFT READY / LIVE WRITE BLOCKED** |
| `feat/phase7-ir-legacy-ac-readiness` | Branch ancestry repaired; diff from Phase 6 is IR runbook/handoff only | RM4 Mini or supported IR hardware + one real AC pilot | **HARDWARE BLOCKED** |
| `feat/phase8-hermes-home-tool-intent-contract` | Intent-policy checks 8/8 PASS | Live execute remains disabled until underlying home tools pass their gates | **DRAFT READY** |
| `feat/phase9-remote-command-security-contract` | Remote-policy checks 8/8 PASS | No public exposure until authenticated transport/authorization/audit validation | **DRAFT READY / LIVE REMOTE BLOCKED** |
| `feat/phase10-home-scene-orchestration` | New Phase 10 scene tests 7/7 PASS; pycompile/diff-check PASS | Real allowlisted HA scene pilot | **DRAFT READY / LIVE SCENE BLOCKED** |
| `codex/hermes-shadow-targeted-tests` / PR #1 | Historical Hermes shadow work exists | Branch is stale/diverged from current master and overlaps later remediation | **NEEDS REBASE/REVIEW — DO NOT MERGE AS-IS** |

## Non-live test totals completed on 2026-08-28

- Phase 1: 7/7
- Phase 2: 6/6
- Phase 3: 6/6
- Phase 4: 6/6
- Phase 5: 7/7
- Phase 6: 8/8
- Phase 8: 8/8
- Phase 9: 8/8
- Phase 10: 7/7

Phase 7 is intentionally documentation/readiness only until IR hardware exists.

## Recommended PR opening order

1. `feat/camera-discovery-tool` -> `master` as an independent PR.
2. `feat/phase0-security-cleanup` -> `master` as Draft until the LG live gate closes.
3. `feat/phase1-stt-provider-abstraction` -> `feat/phase0-security-cleanup`.
4. STT line: Phase 2 -> Phase 1, then Phase 3 -> Phase 2.
5. Home line: Phase 4 -> Phase 1, Phase 5 -> Phase 4, Phase 6 -> Phase 5.
6. Non-IR continuation: Phase 8 -> Phase 6, Phase 9 -> Phase 8, Phase 10 -> Phase 9.
7. IR lane: Phase 7 -> Phase 6 may be opened as Draft/runbook review, but merge remains hardware-gated.

Opening stacked Draft PRs is allowed for review visibility. Merging still follows the live/evidence gates above.

## Current stop lines

Do not claim the following as passed yet:

- LG rotated-key live regression / Phase 0 final gate
- real microphone/STT benchmark dataset
- real Home Assistant onboarding and entity mapping
- real HA side-effect confirmation pilot
- RM4 Mini / legacy AC pilot
- authenticated remote side-effect path
- real Home Assistant scene execution

Prepared code is not equivalent to production-ready evidence.