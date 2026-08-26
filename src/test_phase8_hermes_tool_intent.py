"""Phase 8 Hermes tool-intent contract checks. Validation only; no Hermes/HA runtime required."""
from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday.hermes_tool_intent import HermesToolIntentError, validate_hermes_tool_intent


def make_core(*, gate_write=True):
    tools = {
        "home_device_status": lambda args: "status",
        "home_device_power": lambda args: "power",
        "home_ac_set_temperature": lambda args: "temperature",
        "ha_get_entity_state": lambda args: "raw",
    }
    schemas = [
        {
            "type": "function",
            "function": {
                "name": "home_device_status",
                "parameters": {
                    "type": "object",
                    "properties": {"device": {"type": "string"}},
                    "required": ["device"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "home_device_power",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string"},
                        "action": {"type": "string", "enum": ["on", "off"]},
                    },
                    "required": ["device", "action"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "home_ac_set_temperature",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string"},
                        "temperature": {"type": "number", "minimum": 16, "maximum": 30},
                    },
                    "required": ["device", "temperature"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "ha_get_entity_state",
                "parameters": {
                    "type": "object",
                    "properties": {"entity_id": {"type": "string"}},
                    "required": ["entity_id"],
                },
            },
        },
    ]
    gates = {}
    if gate_write:
        gates["home_device_power"] = {"execute": tools["home_device_power"]}
        gates["home_ac_set_temperature"] = {"execute": tools["home_ac_set_temperature"]}
    return SimpleNamespace(
        TOOLS=tools,
        TOOL_SCHEMAS=schemas,
        CONFIRM_GATED=gates,
        _pack_args=lambda name, args: json.dumps(args, ensure_ascii=False, sort_keys=True),
    )


def payload(tool, arguments):
    return {
        "type": "tool_intent",
        "version": 1,
        "correlation_id": "ffh_test_001",
        "tool": tool,
        "arguments": arguments,
    }


def expect_error(fn, contains):
    try:
        fn()
    except HermesToolIntentError as exc:
        assert contains in str(exc), str(exc)
        return
    raise AssertionError("expected HermesToolIntentError")


def check_read_only_intent_validates_without_confirmation():
    result = validate_hermes_tool_intent(payload("home_device_status", {"device": "แอร์ล่าง"}), make_core())
    assert result.tool_name == "home_device_status"
    assert result.requires_confirmation is False


def check_write_intent_requires_friday_gate():
    result = validate_hermes_tool_intent(
        payload("home_device_power", {"device": "ทีวีล่าง", "action": "on"}), make_core()
    )
    assert result.requires_confirmation is True
    assert "ทีวีล่าง" in result.packed_args


def check_missing_write_gate_rejected():
    expect_error(
        lambda: validate_hermes_tool_intent(
            payload("home_device_power", {"device": "ทีวีล่าง", "action": "on"}),
            make_core(gate_write=False),
        ),
        "missing Friday confirmation gate",
    )


def check_raw_ha_entity_tool_not_allowed():
    expect_error(
        lambda: validate_hermes_tool_intent(
            payload("ha_get_entity_state", {"entity_id": "climate.downstairs_ac"}), make_core()
        ),
        "not allowed",
    )


def check_temperature_range_rejected_before_packing():
    expect_error(
        lambda: validate_hermes_tool_intent(
            payload("home_ac_set_temperature", {"device": "แอร์ล่าง", "temperature": 45}), make_core()
        ),
        "above maximum",
    )


def check_unknown_argument_rejected():
    expect_error(
        lambda: validate_hermes_tool_intent(
            payload("home_device_power", {"device": "ทีวีล่าง", "action": "on", "bypass_confirm": True}),
            make_core(),
        ),
        "unknown arguments",
    )


def check_safety_override_envelope_field_rejected():
    bad = payload("home_device_power", {"device": "ทีวีล่าง", "action": "on"})
    bad["requires_confirmation"] = False
    expect_error(lambda: validate_hermes_tool_intent(bad, make_core()), "unknown tool intent fields")


def check_invalid_envelope_and_correlation_id():
    bad = payload("home_device_status", {"device": "ทีวีล่าง"})
    bad["version"] = 2
    expect_error(lambda: validate_hermes_tool_intent(bad, make_core()), "unsupported tool intent envelope")
    bad = payload("home_device_status", {"device": "ทีวีล่าง"})
    bad["correlation_id"] = "../../bad id"
    expect_error(lambda: validate_hermes_tool_intent(bad, make_core()), "invalid correlation_id")


TESTS = [
    check_read_only_intent_validates_without_confirmation,
    check_write_intent_requires_friday_gate,
    check_missing_write_gate_rejected,
    check_raw_ha_entity_tool_not_allowed,
    check_temperature_range_rejected_before_packing,
    check_unknown_argument_rejected,
    check_safety_override_envelope_field_rejected,
    check_invalid_envelope_and_correlation_id,
]


if __name__ == "__main__":
    failures = []
    for test in TESTS:
        try:
            test()
            print(f"[PASS] {test.__name__}")
        except Exception as exc:
            failures.append((test.__name__, exc))
            print(f"[FAIL] {test.__name__}: {type(exc).__name__}: {exc}")
    if failures:
        raise SystemExit(1)
    print(f"Phase 8 Hermes tool-intent checks passed: {len(TESTS)}/{len(TESTS)}")
