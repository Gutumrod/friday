"""Phase 6 smart-home write-tool checks. All effects are faked; no real HA instance required."""
from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday.home_assistant_client import HomeAssistantClient, HomeAssistantConfig
from friday.home_control_runtime import HOME_WRITE_TOOL_NAMES, install_home_control_tools
from friday.home_device_registry import HomeDeviceRegistry


REGISTRY_PAYLOAD = {
    "version": 1,
    "devices": [
        {
            "id": "living_room_tv",
            "aliases": ["ทีวีล่าง"],
            "entities": {"primary": "media_player.living_room_tv"},
            "capabilities": ["read_state", "power", "media"],
        },
        {
            "id": "downstairs_ac",
            "aliases": ["แอร์ล่าง"],
            "entities": {"primary": "climate.downstairs_ac"},
            "capabilities": ["read_state", "power", "temperature", "mode", "fan"],
        },
    ],
}


class FakeClient:
    def __init__(self):
        self.calls = []

    def call_service(self, domain, service, service_data):
        self.calls.append((domain, service, service_data))
        return []


def make_runtime():
    client = FakeClient()
    registry = HomeDeviceRegistry.from_dict(REGISTRY_PAYLOAD)
    core = SimpleNamespace(
        TOOLS={"get_time": lambda _="": "time"},
        TOOL_SCHEMAS=[{"type": "function", "function": {"name": "get_time", "parameters": {}}}],
        CONFIRM_GATED={},
        _pack_args=lambda name, args: "legacy",
    )
    enabled = install_home_control_tools(core, client=client, registry=registry, emit_warnings=False)
    assert enabled is True
    return core, client


def check_all_write_tools_are_confirm_gated():
    core, _ = make_runtime()
    schema_names = {s["function"]["name"] for s in core.TOOL_SCHEMAS}
    for name in HOME_WRITE_TOOL_NAMES:
        assert name in core.TOOLS
        assert name in schema_names
        assert name in core.CONFIRM_GATED
        assert core.CONFIRM_GATED[name]["execute"] is core.TOOLS[name]
        assert core.CONFIRM_GATED[name]["question"](core._pack_args(name, {}))
        assert core.CONFIRM_GATED[name]["cancel"]("")


def check_tv_power_service_call_after_execute():
    core, client = make_runtime()
    packed = core._pack_args("home_device_power", {"device": "ทีวีล่าง", "action": "on"})
    question = core.CONFIRM_GATED["home_device_power"]["question"](packed)
    assert "ยืนยันไหม" in question and "ทีวีล่าง" in question
    assert client.calls == [], "question construction must not execute the service"
    out = core.CONFIRM_GATED["home_device_power"]["execute"](packed)
    assert client.calls == [
        ("media_player", "turn_on", {"entity_id": "media_player.living_room_tv"})
    ]
    assert "เปิด" in out


def check_temperature_service_call():
    core, client = make_runtime()
    packed = core._pack_args("home_ac_set_temperature", {"device": "แอร์ล่าง", "temperature": 25})
    out = core.CONFIRM_GATED["home_ac_set_temperature"]["execute"](packed)
    assert client.calls == [
        ("climate", "set_temperature", {"entity_id": "climate.downstairs_ac", "temperature": 25.0})
    ]
    assert "25" in out


def check_out_of_range_temperature_never_calls_ha():
    core, client = make_runtime()
    packed = core._pack_args("home_ac_set_temperature", {"device": "แอร์ล่าง", "temperature": 40})
    out = core.CONFIRM_GATED["home_ac_set_temperature"]["execute"](packed)
    assert "16 ถึง 30" in out
    assert client.calls == []


def check_unknown_device_never_calls_ha():
    core, client = make_runtime()
    packed = core._pack_args("home_device_power", {"device": "เครื่องไม่รู้จัก", "action": "on"})
    out = core.CONFIRM_GATED["home_device_power"]["execute"](packed)
    assert "ไม่สำเร็จ" in out
    assert client.calls == []


def check_capability_mismatch_never_calls_ha():
    core, client = make_runtime()
    packed = core._pack_args("home_ac_set_temperature", {"device": "ทีวีล่าง", "temperature": 25})
    out = core.CONFIRM_GATED["home_ac_set_temperature"]["execute"](packed)
    assert "ไม่สำเร็จ" in out
    assert client.calls == []


def check_mode_and_fan_validation():
    core, client = make_runtime()
    bad_mode = core._pack_args("home_ac_set_mode", {"device": "แอร์ล่าง", "mode": "turbo-unknown"})
    assert "ไม่อยู่ในรายการ" in core.CONFIRM_GATED["home_ac_set_mode"]["execute"](bad_mode)
    bad_fan = core._pack_args("home_ac_set_fan_mode", {"device": "แอร์ล่าง", "fan_mode": "warp"})
    assert "ไม่อยู่ในรายการ" in core.CONFIRM_GATED["home_ac_set_fan_mode"]["execute"](bad_fan)
    assert client.calls == []


def check_home_assistant_service_client_posts_json():
    seen = {}

    class Response:
        status_code = 200

        def json(self):
            return []

    class Session:
        def request(self, method, url, **kwargs):
            seen.update({"method": method, "url": url, **kwargs})
            return Response()

    client = HomeAssistantClient(
        HomeAssistantConfig("http://127.0.0.1:8123", "secret-token", 3), session=Session()
    )
    result = client.call_service("climate", "set_temperature", {"entity_id": "climate.ac", "temperature": 25})
    assert result == []
    assert seen["method"] == "POST"
    assert seen["url"].endswith("/api/services/climate/set_temperature")
    assert seen["json"] == {"entity_id": "climate.ac", "temperature": 25}
    assert seen["headers"]["Authorization"] == "Bearer secret-token"


TESTS = [
    check_all_write_tools_are_confirm_gated,
    check_tv_power_service_call_after_execute,
    check_temperature_service_call,
    check_out_of_range_temperature_never_calls_ha,
    check_unknown_device_never_calls_ha,
    check_capability_mismatch_never_calls_ha,
    check_mode_and_fan_validation,
    check_home_assistant_service_client_posts_json,
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
    print(f"Phase 6 smart-home control checks passed: {len(TESTS)}/{len(TESTS)}")
