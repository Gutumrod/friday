from __future__ import annotations

import json
from typing import Any

from friday.home_assistant_client import (
    HomeAssistantClient,
    HomeAssistantConfig,
    HomeAssistantConfigError,
    HomeAssistantError,
)

HA_READ_ONLY_TOOL_NAMES = ("ha_status", "ha_get_entity_state", "ha_list_entities")


def _tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "ha_status",
                "description": "เช็คว่า Home Assistant พร้อมใช้งานหรือไม่ เป็นการอ่านข้อมูลอย่างเดียว",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "ha_get_entity_state",
                "description": "อ่านสถานะ entity ที่อนุญาตจาก Home Assistant โดยใช้ entity_id",
                "parameters": {
                    "type": "object",
                    "properties": {"entity_id": {"type": "string"}},
                    "required": ["entity_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "ha_list_entities",
                "description": "แสดงรายการ Home Assistant entities แบบอ่านอย่างเดียว จำกัดจำนวนผลลัพธ์",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "เช่น climate, media_player, sensor"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                    },
                    "required": [],
                },
            },
        },
    ]


def install_home_assistant_read_tools(
    core_module: Any,
    *,
    client: HomeAssistantClient | None = None,
    emit_warnings: bool = True,
) -> HomeAssistantClient | None:
    """Register read-only HA tools. Missing config leaves Friday unchanged and safe."""
    if client is None:
        try:
            client = HomeAssistantClient(HomeAssistantConfig.from_env())
        except HomeAssistantConfigError as exc:
            if emit_warnings:
                print(f"WARNING Friday Home Assistant: {exc}")
            return None

    def ha_status(_args=""):
        try:
            result = client.health()
            message = result.get("message") or "API พร้อมใช้งาน"
            return f"Home Assistant เชื่อมต่อได้ค่ะ ({message})"
        except HomeAssistantError as exc:
            return f"เชื่อม Home Assistant ไม่สำเร็จค่ะ ({exc})"

    def ha_get_entity_state(args=""):
        entity_id = str(args or "").strip().strip('"')
        if not entity_id:
            return "ต้องระบุ entity_id ค่ะ"
        try:
            state = client.get_entity_state(entity_id)
        except HomeAssistantError as exc:
            return f"อ่านสถานะ {entity_id} ไม่สำเร็จค่ะ ({exc})"
        friendly = (state.get("attributes") or {}).get("friendly_name")
        label = f"{friendly} ({entity_id})" if friendly else entity_id
        return f"{label} ตอนนี้สถานะ {state.get('state', 'unknown')} ค่ะ"

    def ha_list_entities(args=""):
        try:
            packed = json.loads(args) if isinstance(args, str) and args.strip() else {}
        except json.JSONDecodeError:
            packed = {}
        domain = str(packed.get("domain") or "").strip()
        try:
            limit = int(packed.get("limit") or 20)
        except (TypeError, ValueError):
            return "จำนวนรายการ Home Assistant ไม่ถูกต้องค่ะ"
        try:
            states = client.list_entities(domain=domain, limit=limit)
        except HomeAssistantError as exc:
            return f"อ่านรายการ Home Assistant ไม่สำเร็จค่ะ ({exc})"
        if not states:
            suffix = f" ใน domain {domain}" if domain else ""
            return f"ไม่พบ Home Assistant entity{suffix} ค่ะ"
        ids = [str(row.get("entity_id") or "") for row in states if row.get("entity_id")]
        return "Home Assistant entities: " + ", ".join(ids)

    tool_functions = {
        "ha_status": ha_status,
        "ha_get_entity_state": ha_get_entity_state,
        "ha_list_entities": ha_list_entities,
    }
    core_module.TOOLS.update(tool_functions)

    existing_schema_names = {schema["function"]["name"] for schema in core_module.TOOL_SCHEMAS}
    for schema in _tool_schemas():
        if schema["function"]["name"] not in existing_schema_names:
            core_module.TOOL_SCHEMAS.append(schema)

    legacy_pack_args = core_module._pack_args

    def _pack_args(name: str, args: dict[str, Any] | None):
        args = args or {}
        if name == "ha_get_entity_state":
            return str(args.get("entity_id") or "")
        if name == "ha_list_entities":
            return json.dumps(
                {"domain": args.get("domain") or "", "limit": args.get("limit") or 20},
                ensure_ascii=False,
            )
        if name == "ha_status":
            return ""
        return legacy_pack_args(name, args)

    core_module._pack_args = _pack_args

    # Existing prompt says only a fixed historical list is ungated. Extend it explicitly so
    # the model does not expect a confirmation that the executor intentionally does not ask for.
    legacy_build_system_prompt = core_module.build_system_prompt

    def _build_system_prompt():
        return legacy_build_system_prompt() + (
            "\n\nHome Assistant read-only tools ha_status, ha_get_entity_state และ ha_list_entities "
            "เป็นการอ่านข้อมูลอย่างเดียวและไม่ต้องขอยืนยันก่อนใช้ค่ะ"
        )

    core_module.build_system_prompt = _build_system_prompt

    if emit_warnings:
        print(f"Friday Home Assistant read-only tools enabled: {client.config.base_url}")
    return client
