"""Phase 5 logical device registry checks. No Home Assistant server required."""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday.home_device_registry import (
    HomeDeviceRegistry,
    HomeDeviceRegistryError,
    UnsupportedCapability,
    UnknownHomeDevice,
    normalize_device_alias,
)
from friday.home_device_runtime import install_home_device_read_tools


PAYLOAD = {
    "version": 1,
    "devices": [
        {
            "id": "living_room_tv",
            "aliases": ["ทีวีห้องนั่งเล่น", "ทีวีล่าง", "Living Room TV"],
            "room": "living_room",
            "entities": {"primary": "media_player.living_room_tv"},
            "capabilities": ["read_state", "power", "media"],
        },
        {
            "id": "downstairs_ac",
            "aliases": ["แอร์ชั้นล่าง", "แอร์ล่าง"],
            "room": "downstairs",
            "entities": {"primary": "climate.downstairs_ac"},
            "capabilities": ["read_state", "power", "temperature", "mode", "fan"],
        },
    ],
}


def check_alias_normalization():
    assert normalize_device_alias(" Living-Room_TV ") == "livingroomtv"
    assert normalize_device_alias("ทีวี ห้องนั่งเล่น") == "ทีวีห้องนั่งเล่น"


def check_resolve_thai_english_and_id():
    registry = HomeDeviceRegistry.from_dict(PAYLOAD)
    assert registry.resolve("ทีวีล่าง").id == "living_room_tv"
    assert registry.resolve("living room tv").id == "living_room_tv"
    assert registry.resolve("downstairs_ac").primary_entity_id == "climate.downstairs_ac"


def check_unknown_device_rejected():
    registry = HomeDeviceRegistry.from_dict(PAYLOAD)
    try:
        registry.resolve("เครื่องชงกาแฟ")
    except UnknownHomeDevice:
        return
    raise AssertionError("unknown alias must not be guessed")


def check_duplicate_alias_rejected():
    payload = {
        "version": 1,
        "devices": [
            {"id": "a", "aliases": ["ทีวี"], "entities": {"primary": "media_player.a"}, "capabilities": ["read_state"]},
            {"id": "b", "aliases": ["ทีวี"], "entities": {"primary": "media_player.b"}, "capabilities": ["read_state"]},
        ],
    }
    try:
        HomeDeviceRegistry.from_dict(payload)
    except HomeDeviceRegistryError as exc:
        assert "ambiguous alias" in str(exc)
        return
    raise AssertionError("ambiguous aliases must fail registry load")


def check_capability_gate():
    registry = HomeDeviceRegistry.from_dict(PAYLOAD)
    assert registry.require_capability("แอร์ล่าง", "temperature").id == "downstairs_ac"
    try:
        registry.require_capability("ทีวีล่าง", "temperature")
    except UnsupportedCapability:
        return
    raise AssertionError("unsupported capability must fail closed")


def check_entity_allowlist():
    registry = HomeDeviceRegistry.from_dict(PAYLOAD)
    assert registry.allowed_entity_ids() == {"media_player.living_room_tv", "climate.downstairs_ac"}


def check_semantic_status_runtime():
    registry = HomeDeviceRegistry.from_dict(PAYLOAD)

    class FakeClient:
        def get_entity_state(self, entity_id):
            assert entity_id == "climate.downstairs_ac"
            return {"entity_id": entity_id, "state": "cool", "attributes": {"friendly_name": "แอร์ชั้นล่าง"}}

    core = SimpleNamespace(
        TOOLS={},
        TOOL_SCHEMAS=[],
        _pack_args=lambda name, args: "legacy",
        build_system_prompt=lambda: "base",
    )
    installed = install_home_device_read_tools(core, client=FakeClient(), registry=registry, emit_warnings=False)
    assert installed is registry
    assert "home_device_status" in core.TOOLS
    assert core._pack_args("home_device_status", {"device": "แอร์ล่าง"}) == "แอร์ล่าง"
    assert core._pack_args("something_else", {}) == "legacy"
    output = core.TOOLS["home_device_status"]("แอร์ล่าง")
    assert "cool" in output and "แอร์ชั้นล่าง" in output
    prompt = core.build_system_prompt()
    assert "ห้ามเดา raw Home Assistant entity_id" in prompt
    assert "แอร์ชั้นล่าง" in prompt


TESTS = [
    check_alias_normalization,
    check_resolve_thai_english_and_id,
    check_unknown_device_rejected,
    check_duplicate_alias_rejected,
    check_capability_gate,
    check_entity_allowlist,
    check_semantic_status_runtime,
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
    print(f"Phase 5 home device registry checks passed: {len(TESTS)}/{len(TESTS)}")
