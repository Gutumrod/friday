# Phase 8 — Hermes Home Tool-Intent Contract

Date: 2026-08-26
Branch: `feat/phase8-hermes-home-tool-intent-contract`
Parent: `feat/phase6-smart-home-confirm-gated-tools`
Status: **VALIDATOR READY — LIVE HERMES EXECUTION NOT WIRED**

## Purpose

Prepare the safety boundary for future Hermes `tool_intent` without allowing Hermes to execute Home Assistant or Friday tools directly.

## Contract

Accepted envelope:

```json
{
  "type": "tool_intent",
  "version": 1,
  "correlation_id": "ffh_...",
  "tool": "home_device_power",
  "arguments": {
    "device": "ทีวีล่าง",
    "action": "on"
  }
}
```

Only the declared envelope fields are allowed. Hermes cannot include a safety override such as `requires_confirmation=false`.

## Friday Authority

Friday determines:

- whether the tool exists
- whether the tool is in the explicit Hermes home allowlist
- argument type/enum/range validity from Friday's current tool schema
- whether confirmation is required from Friday's live `CONFIRM_GATED`
- how arguments are packed for the existing executor

For all home write tools, absence of a Friday confirmation gate is a hard validation error.

## Home Intent Allowlist

- `home_device_status`
- `home_device_power`
- `home_ac_set_temperature`
- `home_ac_set_mode`
- `home_ac_set_fan_mode`

Raw Home Assistant tools/entity IDs are intentionally excluded so Hermes remains at the logical-device layer.

## Implemented

- `src/friday/hermes_tool_intent.py`
- strict v1 envelope validation
- correlation ID validation
- envelope unknown-field rejection
- explicit tool allowlist
- live Friday tool/schema presence checks
- required/unknown argument checks
- string/number/integer/boolean checks
- enum and min/max checks
- argument size limit
- mandatory confirm-gate check for home write tools
- returns `ValidatedToolIntent`; never executes
- `src/test_phase8_hermes_tool_intent.py`

## Stop Line

Do not connect Hermes WebSocket responses to this validator/executor yet. Existing Friday/Hermes plan still requires speak-only sync evidence before live `tool_intent` delegation.
