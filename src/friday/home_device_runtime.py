from __future__ import annotations

from typing import Any

from friday.home_assistant_client import HomeAssistantClient, HomeAssistantError
from friday.home_device_registry import HomeDeviceRegistry, HomeDeviceRegistryError


def install_home_device_read_tools(
    core_module: Any,
    *,
    client: HomeAssistantClient | None,
    registry: HomeDeviceRegistry | None = None,
    emit_warnings: bool = True,
) -> HomeDeviceRegistry | None:
    """Expose semantic device aliases while keeping Phase 5 completely read-only."""
    if client is None:
        return None
    if registry is None:
        try:
            registry = HomeDeviceRegistry.from_env()
        except HomeDeviceRegistryError as exc:
            if emit_warnings:
                print(f"WARNING Friday home device registry: {exc}")
            return None

    def home_device_status(args=""):
        alias = str(args or "").strip().strip('"')
        if not alias:
            return "ต้องบอกชื่ออุปกรณ์ที่ต้องการเช็คค่ะ"
        try:
            device = registry.resolve(alias)
            state = client.get_entity_state(device.primary_entity_id)
        except (HomeDeviceRegistryError, HomeAssistantError) as exc:
            return f"เช็คอุปกรณ์ '{alias}' ไม่สำเร็จค่ะ ({exc})"
        friendly = (state.get("attributes") or {}).get("friendly_name")
        label = friendly or device.id
        return f"{label} ตอนนี้สถานะ {state.get('state', 'unknown')} ค่ะ"

    core_module.TOOLS["home_device_status"] = home_device_status
    if not any(schema["function"]["name"] == "home_device_status" for schema in core_module.TOOL_SCHEMAS):
        core_module.TOOL_SCHEMAS.append(
            {
                "type": "function",
                "function": {
                    "name": "home_device_status",
                    "description": "อ่านสถานะอุปกรณ์ในบ้านจากชื่อเรียกธรรมชาติ เช่น แอร์ชั้นล่าง หรือ ทีวีห้องนั่งเล่น",
                    "parameters": {
                        "type": "object",
                        "properties": {"device": {"type": "string"}},
                        "required": ["device"],
                    },
                },
            }
        )

    legacy_pack_args = core_module._pack_args

    def _pack_args(name: str, args: dict[str, Any] | None):
        args = args or {}
        if name == "home_device_status":
            return str(args.get("device") or "")
        return legacy_pack_args(name, args)

    core_module._pack_args = _pack_args

    legacy_build_system_prompt = core_module.build_system_prompt

    def _build_system_prompt():
        aliases = []
        for device in registry.list_devices():
            aliases.append(f"{device.id}: {', '.join(device.aliases) if device.aliases else device.id}")
        return legacy_build_system_prompt() + (
            "\n\nเมื่อต้องการเช็คสถานะอุปกรณ์ในบ้าน ให้ใช้ home_device_status กับชื่อ logical/alias "
            "ห้ามเดา raw Home Assistant entity_id เอง รายการอุปกรณ์ที่อนุญาต: " + "; ".join(aliases)
        )

    core_module.build_system_prompt = _build_system_prompt

    if emit_warnings:
        print(f"Friday logical home devices enabled: {len(registry.list_devices())}")
    return registry
