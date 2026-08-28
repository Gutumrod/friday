# Friday Work Lanes — IR vs Non-IR

**Date:** 2026-08-28  
**Repository:** `Gutumrod/friday`  
**Decision:** Development continues on all non-IR work immediately. IR-dependent live validation waits for the IR blaster hardware.

## Hardware Decision

Initial IR pilot hardware: **BroadLink RM4 mini** or equivalent Home Assistant-supported IR blaster.

Target IR path:

```text
Friday
 -> Friday policy / Confirm Gate
 -> Home Assistant
 -> climate / logical entity
 -> BroadLink RM4 mini
 -> IR
 -> legacy AC or other IR-only appliance
```

Friday must not own raw IR codes in its intent layer or source tree.

## Lane A — Non-IR: Start Now

These items do **not** require the RM4 mini and should continue without waiting for hardware:

1. **Phase 0 — Security / machine config**
   - secret/config cleanup
   - Hermes redaction fix
   - LG webOS credential rotation/re-pairing
   - direct LG TV regression and state verification
   - DHCP/IP-discovery mitigation or transition behind Home Assistant

2. **Phase 1 — STT provider abstraction**
   - Google/Typhoon provider contract and runtime validation

3. **Phase 2 — STT benchmark harness**
   - real owner-speech dataset and benchmark evidence

4. **Phase 3 — Streaming STT contract**
   - contract/testing work; production adoption remains evidence-gated by Phase 2

5. **Phase 4 — Home Assistant foundation**
   - install/connect Home Assistant
   - add LG webOS TV
   - verify read-only entity/state/media metadata
   - Home Assistant onboarding must not wait for IR hardware

6. **Phase 5 — Logical home device registry**
   - aliases, capabilities, entity mapping, fail-closed behavior

7. **Phase 6 — Confirm-gated smart-home writes**
   - policy/schema/service-call layer can be validated with non-IR HA devices
   - LG TV or another low-risk HA entity may be used for live write evidence
   - AC-specific physical verification is deferred to the IR lane

8. **Phase 8 — Hermes home tool-intent contract**
   - Hermes proposes intent; Friday validates and retains confirmation authority

9. **Phase 9 — Remote command security contract**
   - authentication, authorization, audit/replay policy

10. **Phase 10 — Scene orchestration**
    - scenes containing only available non-IR entities can be validated now
    - scenes that require an IR appliance remain partially blocked until IR hardware exists

11. **LG TV integration work**
    - direct webOS compatibility path
    - Home Assistant media_player migration
    - power/app/media state and playback orchestration

12. **Tapo C210 camera work**
    - LAN discovery
    - Home Assistant/Tapo integration exploration
    - read-only state/capability discovery
    - later camera side effects require their own Friday Confirm Gate

## Lane B — IR-Dependent: Wait for Hardware

The following live acceptance work requires the RM4 mini (or equivalent) to be physically present:

1. **Phase 7 — Legacy AC / IR readiness live gate**
2. Pair/setup the IR blaster in Home Assistant
3. Learn or map the real AC remote commands
4. Expose the AC through a Home Assistant climate/logical abstraction
5. Verify real physical behavior:
   - power
   - temperature
   - HVAC mode
   - fan mode where supported
6. Determine state confidence when the appliance cannot report authoritative state
7. Validate one-room / one-AC pilot before expanding to other IR appliances
8. Validate scenes whose success depends on an IR-controlled device
9. Add future IR-only fans/TV boxes/appliances only after the one-AC path is stable

## Merge / PR Rule

IR hardware is **not** a prerequisite for merging independent non-IR work when that branch's own runtime/security gate has passed.

Do not mark IR-dependent physical acceptance as passed using mocks or command-sent evidence alone.

## Execution Order From Today

```text
NOW
 -> finish Phase 0 live gate
 -> Phase 1 runtime gate
 -> Phase 2 benchmark
 -> Phase 3 decision gate
 -> Home Assistant Phase 4
 -> Phase 5 registry
 -> Phase 6 non-IR live write evidence
 -> Phase 8
 -> Phase 9
 -> Phase 10 non-IR scenes

WHEN RM4 MINI ARRIVES
 -> repair/rebase Phase 7 branch if needed
 -> HA BroadLink setup
 -> one-AC IR pilot
 -> physical-state/confidence evidence
 -> IR-dependent scenes and additional appliances
```

This split is authoritative for scheduling: **do not let IR hardware block the non-IR roadmap.**