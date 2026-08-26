"""Phase 4 Home Assistant client/runtime checks. No Home Assistant server required."""
from __future__ import annotations

import json
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday.home_assistant_client import HomeAssistantClient, HomeAssistantConfig, HomeAssistantError
from friday.home_assistant_runtime import install_home_assistant_read_tools


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def request(self, method, url, headers=None, timeout=None):
        self.calls.append({"method": method, "url": url, "headers": headers or {}, "timeout": timeout})
        path = url.split("8123", 1)[-1]
        status, payload = self.routes.get((method, path), (404, {"message": "missing"}))
        return FakeResponse(status, payload)


def make_client():
    session = FakeSession(
        {
            ("GET", "/api/"): (200, {"message": "API running."}),
            ("GET", "/api/states/climate.downstairs_ac"): (
                200,
                {
                    "entity_id": "climate.downstairs_ac",
                    "state": "cool",
                    "attributes": {"friendly_name": "แอร์ชั้นล่าง", "temperature": 25},
                },
            ),
            ("GET", "/api/states"): (
                200,
                [
                    {"entity_id": "climate.downstairs_ac", "state": "cool", "attributes": {}},
                    {"entity_id": "media_player.living_room_tv", "state": "on", "attributes": {}},
                    {"entity_id": "sensor.room_temperature", "state": "27.1", "attributes": {}},
                ],
            ),
        }
    )
    config = HomeAssistantConfig("http://127.0.0.1:8123", "super-secret-token", 2.5)
    return HomeAssistantClient(config, session=session), session


def check_auth_header_and_secret_repr():
    client, session = make_client()
    result = client.health()
    assert result["ok"] is True
    call = session.calls[0]
    assert call["headers"]["Authorization"] == "Bearer super-secret-token"
    assert "super-secret-token" not in repr(client)
    assert "super-secret-token" not in repr(client.config)


def check_get_entity_state():
    client, _ = make_client()
    state = client.get_entity_state("climate.downstairs_ac")
    assert state["state"] == "cool"
    assert state["attributes"]["temperature"] == 25


def check_list_entities_filter_limit():
    client, _ = make_client()
    climate = client.list_entities(domain="climate", limit=10)
    assert [row["entity_id"] for row in climate] == ["climate.downstairs_ac"]
    first_two = client.list_entities(limit=2)
    assert len(first_two) == 2


def check_entity_validation():
    client, _ = make_client()
    try:
        client.get_entity_state("not-an-entity")
    except HomeAssistantError as exc:
        assert str(exc) == "invalid_entity_id"
    else:
        raise AssertionError("invalid entity id must be rejected before HTTP")


def check_runtime_wires_read_only_tools_without_confirm_gate():
    client, _ = make_client()

    def legacy_pack(name, args):
        return "legacy"

    core = SimpleNamespace(
        TOOLS={"get_time": lambda _="": "time"},
        TOOL_SCHEMAS=[{"type": "function", "function": {"name": "get_time", "parameters": {}}}],
        CONFIRM_GATED={},
        _pack_args=legacy_pack,
        build_system_prompt=lambda: "base prompt",
    )
    installed = install_home_assistant_read_tools(core, client=client, emit_warnings=False)
    assert installed is client
    for name in ("ha_status", "ha_get_entity_state", "ha_list_entities"):
        assert name in core.TOOLS
        assert name not in core.CONFIRM_GATED

    assert "เชื่อมต่อได้" in core.TOOLS["ha_status"]("")
    assert "แอร์ชั้นล่าง" in core.TOOLS["ha_get_entity_state"]("climate.downstairs_ac")
    packed = core._pack_args("ha_list_entities", {"domain": "climate", "limit": 5})
    assert json.loads(packed) == {"domain": "climate", "limit": 5}
    listed = core.TOOLS["ha_list_entities"](packed)
    assert "climate.downstairs_ac" in listed
    assert core._pack_args("get_time", {}) == "legacy"
    assert "ไม่ต้องขอยืนยัน" in core.build_system_prompt()


def check_missing_env_leaves_runtime_unchanged():
    saved_url = os.environ.pop("HOME_ASSISTANT_URL", None)
    saved_token = os.environ.pop("HOME_ASSISTANT_TOKEN", None)
    try:
        core = SimpleNamespace(
            TOOLS={}, TOOL_SCHEMAS=[], CONFIRM_GATED={}, _pack_args=lambda n, a: "", build_system_prompt=lambda: "base"
        )
        result = install_home_assistant_read_tools(core, emit_warnings=False)
        assert result is None
        assert core.TOOLS == {} and core.TOOL_SCHEMAS == []
    finally:
        if saved_url is not None:
            os.environ["HOME_ASSISTANT_URL"] = saved_url
        if saved_token is not None:
            os.environ["HOME_ASSISTANT_TOKEN"] = saved_token


TESTS = [
    check_auth_header_and_secret_repr,
    check_get_entity_state,
    check_list_entities_filter_limit,
    check_entity_validation,
    check_runtime_wires_read_only_tools_without_confirm_gate,
    check_missing_env_leaves_runtime_unchanged,
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
    print(f"Phase 4 Home Assistant checks passed: {len(TESTS)}/{len(TESTS)}")
