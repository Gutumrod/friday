# Phase 6 — Confirm-Gated Smart-Home Controls Evidence

Date: 2026-08-26
Branch: `feat/phase6-smart-home-confirm-gated-tools`
Parent: `feat/phase5-home-device-registry`
Status: **CODE COMPLETE — BLOCKED FROM MERGE BY LIVE PHASE 4/5 GATES**

## Safety Model

All Home Assistant write tools are added to `CONFIRM_GATED` at registration time. The LLM never receives an enabled write tool without a matching confirmation gate.

Every write request:

1. accepts a logical device alias, not arbitrary raw entity ID
2. resolves through the local device registry
3. validates required capability
4. validates command/range
5. asks for owner confirmation
6. only after confirmation calls Home Assistant `/api/services/<domain>/<service>`

## Implemented Write Tools

- `home_device_power` — `turn_on` / `turn_off`
- `home_ac_set_temperature` — climate `set_temperature`, hard range 16-30 C
- `home_ac_set_mode` — climate `set_hvac_mode`, allowlisted modes
- `home_ac_set_fan_mode` — climate `set_fan_mode`, conservative allowlist

## Home Assistant Client Change

Added validated `call_service(domain, service, service_data)` using authenticated POST to the Home Assistant services endpoint.

No use of `POST /api/states` for physical device control.

## Negative Coverage

`src/test_phase6_home_control.py` verifies:

- all write tools are confirm-gated
- constructing confirmation text causes zero HA calls
- power service mapping
- temperature service mapping
- temperature outside 16-30 never calls HA
- unknown logical device never calls HA
- capability mismatch never calls HA
- invalid HVAC/fan modes never call HA
- service client posts expected JSON payload

## Merge Stop Line

Do not open/merge this branch until:

- Phase 0 security live gate passes
- Phase 4 real Home Assistant read-only gate passes
- Phase 5 logical alias mapping is verified against real entities
- TV or another low-risk pilot validates the confirmation UX

Legacy AC/IR hardware remains Phase 7.
