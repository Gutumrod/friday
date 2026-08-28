from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday.home_scene_registry import (
    HomeSceneRegistry,
    HomeSceneRegistryError,
    UnknownHomeScene,
)
from friday.home_scene_runtime import install_home_scene_tools


SCENE_PAYLOAD = {
    "version": 1,
    "scenes": [
        {
            "id": "arriving_home",
            "aliases": ["กลับบ้าน", "ถึงบ้าน"],
            "entity_id": "scene.arriving_home",
            "description": "Low-risk arrival scene",
        },
        {
            "id": "bedtime",
            "aliases": ["เข้านอน"],
            "entity_id": "scene.bedtime",
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
    registry = HomeSceneRegistry.from_dict(SCENE_PAYLOAD)
    core = SimpleNamespace(
        TOOLS={"get_time": lambda _="": "time"},
        TOOL_SCHEMAS=[{"type": "function", "function": {"name": "get_time", "parameters": {}}}],
        CONFIRM_GATED={},
        _pack_args=lambda name, args: "legacy",
        build_system_prompt=lambda: "BASE",
    )
    enabled = install_home_scene_tools(core, client=client, registry=registry, emit_warnings=False)
    assert enabled is registry
    return core, client, registry


def check_registry_resolves_ids_and_aliases():
    registry = HomeSceneRegistry.from_dict(SCENE_PAYLOAD)
    assert registry.resolve("arriving_home").entity_id == "scene.arriving_home"
    assert registry.resolve("  กลับบ้าน  ").id == "arriving_home"
    assert registry.resolve("เข้านอน").id == "bedtime"


def check_registry_rejects_invalid_or_ambiguous_scenes():
    bad_entity = {"version": 1, "scenes": [{"id": "x", "aliases": [], "entity_id": "script.x"}]}
    try:
        HomeSceneRegistry.from_dict(bad_entity)
        raise AssertionError("non-scene entity should be rejected")
    except HomeSceneRegistryError:
        pass

    duplicate_alias = {
        "version": 1,
        "scenes": [
            {"id": "a", "aliases": ["same"], "entity_id": "scene.a"},
            {"id": "b", "aliases": ["same"], "entity_id": "scene.b"},
        ],
    }
    try:
        HomeSceneRegistry.from_dict(duplicate_alias)
        raise AssertionError("ambiguous alias should be rejected")
    except HomeSceneRegistryError:
        pass


def check_unknown_scene_fails_closed():
    registry = HomeSceneRegistry.from_dict(SCENE_PAYLOAD)
    try:
        registry.resolve("ไม่มีฉากนี้")
        raise AssertionError("unknown scene should be rejected")
    except UnknownHomeScene:
        pass


def check_scene_activation_is_confirm_gated():
    core, client, _ = make_runtime()
    schema_names = {s["function"]["name"] for s in core.TOOL_SCHEMAS}
    assert "home_scene_list" in core.TOOLS
    assert "home_scene_activate" in core.TOOLS
    assert {"home_scene_list", "home_scene_activate"} <= schema_names
    assert "home_scene_list" not in core.CONFIRM_GATED
    assert "home_scene_activate" in core.CONFIRM_GATED
    packed = core._pack_args("home_scene_activate", {"scene": "กลับบ้าน"})
    question = core.CONFIRM_GATED["home_scene_activate"]["question"](packed)
    assert "ยืนยันไหม" in question and "กลับบ้าน" in question
    assert client.calls == [], "confirmation question must not execute scene"


def check_confirmed_activation_calls_only_allowlisted_entity():
    core, client, _ = make_runtime()
    packed = core._pack_args("home_scene_activate", {"scene": "กลับบ้าน"})
    out = core.CONFIRM_GATED["home_scene_activate"]["execute"](packed)
    assert client.calls == [("scene", "turn_on", {"entity_id": "scene.arriving_home"})]
    assert "Home Assistant" in out
    client.calls.clear()
    bad = core.CONFIRM_GATED["home_scene_activate"]["execute"]("scene.evil")
    assert "ไม่สำเร็จ" in bad
    assert client.calls == []


def check_prompt_lists_allowlisted_aliases_only():
    core, _, _ = make_runtime()
    prompt = core.build_system_prompt()
    assert "arriving_home" in prompt and "กลับบ้าน" in prompt and "bedtime" in prompt
    assert "สร้าง automation rule ใหม่เอง" in prompt


def check_missing_registry_leaves_runtime_unchanged():
    core = SimpleNamespace(
        TOOLS={"get_time": lambda _="": "time"},
        TOOL_SCHEMAS=[{"type": "function", "function": {"name": "get_time", "parameters": {}}}],
        CONFIRM_GATED={},
        _pack_args=lambda name, args: "legacy",
        build_system_prompt=lambda: "BASE",
    )
    old = os.environ.get("HOME_SCENE_REGISTRY_PATH")
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["HOME_SCENE_REGISTRY_PATH"] = str(Path(tmp) / "missing.json")
        try:
            result = install_home_scene_tools(core, client=FakeClient(), emit_warnings=False)
        finally:
            if old is None:
                os.environ.pop("HOME_SCENE_REGISTRY_PATH", None)
            else:
                os.environ["HOME_SCENE_REGISTRY_PATH"] = old
    assert result is None
    assert set(core.TOOLS) == {"get_time"}
    assert core.CONFIRM_GATED == {}


TESTS = [
    check_registry_resolves_ids_and_aliases,
    check_registry_rejects_invalid_or_ambiguous_scenes,
    check_unknown_scene_fails_closed,
    check_scene_activation_is_confirm_gated,
    check_confirmed_activation_calls_only_allowlisted_entity,
    check_prompt_lists_allowlisted_aliases_only,
    check_missing_registry_leaves_runtime_unchanged,
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
    print(f"Phase 10 home-scene checks passed: {len(TESTS)}/{len(TESTS)}")
