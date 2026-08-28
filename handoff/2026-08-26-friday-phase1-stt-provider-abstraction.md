# Friday Phase 1 STT Provider Abstraction Handoff

Date: 2026-08-26
Branch: `feat/phase1-stt-provider-abstraction`
Parent branch: `feat/phase0-security-cleanup`
Status: CODE COMPLETE / LIVE GATE PENDING

## Read First

1. `AGENTS.md`
2. this file
3. `docs/PHASE1_STT_PROVIDER_EVIDENCE_2026-08-26.md`
4. `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`
5. Phase 0 evidence/handoff

## Current Behavior

Production default remains Google STT. `FRIDAY_STT_PROVIDER=google` is the safe default.

The launcher now installs a provider adapter before starting the existing voice loop. The old `core._recognize_speech()` remains present as rollback until live parity is proven.

Typhoon exists only as an optional non-streaming provider adapter. Do not add it to the base Windows dependency set until its runtime is verified on the target platform.

## Next Work

Use a separate Phase 2 branch for benchmark tooling/data manifests. Do not implement true streaming microphone changes before benchmark evidence.

Home Assistant work is independent of the STT benchmark and should branch from the latest stable code branch rather than depending on an unverified streaming branch.
