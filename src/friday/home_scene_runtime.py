from __future__ import annotations

from typing import Any

from friday.home_assistant_client import HomeAssistantClient, HomeAssistantError
from friday.home_scene_registry import HomeSceneRegistry, HomeSceneRegistryError


def install_home_scene_tools(
    core_module: Any,
    *,
    client: HomeAssistantClient | None,
    registry: HomeSceneRegistry | None = None,
    emit_warnings: bool = True,
) -> HomeSceneRegistry | None:
    """Register logical Home Assistant scenes.

    Listing is read-only. Activation is always wired through Friday's existing Confirm Gate.
    """
    if client is None:
        return None
    if registry is None:
        try:
            registry = HomeSceneRegistry.from_env()
        except HomeSceneRegistryError as exc:
            if emit_warnings:
                print(f"WARNING Friday home scene registry: {exc}")
            return None

    def home_scene_list(_args=""):
        rows = []
        for scene in registry.list_scenes():
            aliases = ", ".join(scene.aliases) if scene.aliases else scene.id
            rows.append(f"{scene.id} ({aliases})")
        return "Home scenes: " + "; ".join(rows)

    def home_scene_activate(args=""):
        alias = str(args or "").strip().strip('"')
        if not alias:
            return "ต้องบอกชื่อ scene ที่ต้องการเปิดค่ะ"
        try:
            scene = registry.resolve(alias)
            client.call_service("scene", "turn_on", {"entity_id": scene.entity_id})
        except (HomeSceneRegistryError, HomeAssistantError) as exc:
            return f"ส่งคำสั่งเปิด scene '{alias}' ไม่สำเร็จค่ะ ({exc})"
        return f"ส่งคำสั่งเปิด scene {scene.id} ไปที่ Home Assistant แล้วค่ะ"

    core_module.TOOLS["home_scene_list"] = home_scene_list
    core_module.TOOLS["home_scene_activate"] = home_scene_activate

    schemas = [
        {
            "type": "function",
            "function": {
                "name": "home_scene_list",
                "description": "ดูรายการ scene ในบ้านที่ Friday ได้รับอนุญาตให้เรียก เป็นการอ่านอย่างเดียว",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "home_scene_activate",
                "description": "เปิด Home Assistant scene จาก logical scene alias เช่น กำลังกลับบ้าน หรือ เข้านอน",
                "parameters": {
                    "type": "object",
                    "properties": {"scene": {"type": "string"}},
                    "required": ["scene"],
                },
            },
        },
    ]
    existing = {schema["function"]["name"] for schema in core_module.TOOL_SCHEMAS}
    for schema in schemas:
        if schema["function"]["name"] not in existing:
            core_module.TOOL_SCHEMAS.append(schema)

    legacy_pack_args = core_module._pack_args

    def _pack_args(name: str, args: dict[str, Any] | None):
        args = args or {}
        if name == "home_scene_list":
            return ""
        if name == "home_scene_activate":
            return str(args.get("scene") or "")
        return legacy_pack_args(name, args)

    core_module._pack_args = _pack_args

    core_module.CONFIRM_GATED["home_scene_activate"] = {
        "question": lambda args: f"ต้องการเปิด scene {args or 'ที่เลือก'} นะคะ ยืนยันไหมคะ",
        "cancel": lambda args: f"ยกเลิกการเปิด scene {args or 'ที่เลือก'} แล้วค่ะ",
        "execute": home_scene_activate,
    }

    legacy_build_system_prompt = core_module.build_system_prompt

    def _build_system_prompt():
        aliases = []
        for scene in registry.list_scenes():
            aliases.append(f"{scene.id}: {', '.join(scene.aliases) if scene.aliases else scene.id}")
        return legacy_build_system_prompt() + (
            "\n\nHome Assistant scenes ที่อนุญาต: " + "; ".join(aliases) +
            " หากต้องการเรียก scene ให้ใช้ home_scene_activate และต้องรอระบบขอยืนยันก่อนเสมอ "
            "Friday ไม่ควรสร้าง automation rule ใหม่เองจากบทสนทนา"
        )

    core_module.build_system_prompt = _build_system_prompt

    if emit_warnings:
        print(f"Friday Home Assistant scenes enabled: {len(registry.list_scenes())}")
    return registry
