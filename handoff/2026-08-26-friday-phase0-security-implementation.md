# Friday Phase 0 Security Implementation Handoff

Date: 2026-08-26
Repo: `Gutumrod/friday`
Branch: `master`
Status: **CODE COMPLETE / LIVE GATE PENDING**

## Read First Next Session

1. `AGENTS.md`
2. `handoff/2026-08-26-friday-phase0-security-implementation.md`
3. `docs/PHASE0_SECURITY_IMPLEMENTATION_EVIDENCE_2026-08-26.md`
4. `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`

## What Changed

Phase 0 implementation was authorized and completed on the repository side.

- LG webOS paired client key removed from current source.
- TV IP/MAC/broadcast config moved to environment-only runtime config.
- Google Cloud credential path no longer has a workstation-specific source default.
- device/camera indexes can be runtime-configured.
- `.env.example` now documents placeholder-only machine-local values.
- `src/friday/runtime_security.py` adds safe startup diagnostics and fail-closed TV guards.
- voice launcher applies runtime guards before `core.main()`.
- API now launches through `friday.api_launcher:app`, which applies the same guards.
- `src/test_phase0_security.py` added for stdlib-only security regression.
- detailed evidence is in `docs/PHASE0_SECURITY_IMPLEMENTATION_EVIDENCE_2026-08-26.md`.

## Critical Security Note

The old TV client key existed in public Git history. Removing it from the current tree is not enough to make that historical key private again.

Before re-enabling TV control locally:

- re-pair/rotate the LG webOS client key
- store only the new key in local `.env`
- never commit `.env`

Do not reuse the historical key.

## Current Stop Line

Both registered development devices were offline during this implementation. Therefore full Windows/TV regression could not be executed.

Gate 0 is **NOT PASS yet**.

When the Windows machine is online:

1. `git pull`
2. populate local `.env`
3. re-pair TV and store new client key
4. run `python src/test_phase0_security.py`
5. run `python src/test_tools.py`
6. live-test TV power/volume/app/remote controls
7. run API launcher and verify status/tools/confirm flow
8. update evidence + this handoff with final Gate 0 verdict

## Next Phase

Phase 1 — STT Provider Abstraction is planned but remains blocked until Phase 0 live regression passes and the owner approves the next implementation phase.
