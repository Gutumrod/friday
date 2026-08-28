# Phase 5 — Logical Home Device Registry Evidence

Date: 2026-08-26
Branch: `feat/phase5-home-device-registry`
Parent: `feat/phase4-home-assistant-foundation`
Status: **CODE COMPLETE — LOCAL/LIVE GATE PENDING**

## Implemented

- Versioned JSON logical device registry.
- Stable logical IDs independent of vendor/IP/MAC.
- Thai/English aliases.
- normalized alias resolution.
- duplicate/ambiguous aliases fail registry load.
- unknown aliases fail closed; Friday must not guess raw entity IDs.
- per-device entity mapping with required `primary` entity.
- capability allowlist and `require_capability()`.
- allowed Home Assistant entity set derivation.
- local `home_devices.json` ignored; committed `home_devices.example.json` contains only examples.
- semantic read-only `home_device_status` tool for Friday voice/API runtimes.
- registry aliases are added to the system prompt so the LLM selects logical names rather than inventing entity IDs.
- `src/test_phase5_home_device_registry.py` covers aliasing, ambiguity, unknown devices, capabilities, allowlist, and runtime wiring.

## Gate

Copy `home_devices.example.json` to ignored `home_devices.json`, replace example entity IDs with real Home Assistant entities, and verify semantic status against a real TV/other entity before merge.

No write capability is enabled by this phase.
