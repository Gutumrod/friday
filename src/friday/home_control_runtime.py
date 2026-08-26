from __future__ import annotations

import json
from typing import Any

from friday.home_assistant_client import HomeAssistantClient, HomeAssistantError
from friday.home_device_registry import HomeDeviceRegistry, HomeDeviceRegistryError

HOME_WRITE_TOOL_NAMES = (
    "home_device_power",
    "home_ac_set_temperature",
    "home_ac_set_mode",
    "home_ac_set_fan_mode",
)

_ALLOWED_HVAC_MODES = {"auto", "cool", "dry", "fan_only", "heat", "heat_cool", "off"}
_ALLOWED_FAN_MODES = {"auto", "low", "medium", "high"}


def _parse(args: str) -> dict[str, Any]:
    try:
        value = json.loads(args or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("invalid tool arguments") from exc
    if not isinstance(value, dict):
        raise ValueError("invalid tool arguments")
    return value


def _entity_domain(entity_id: str) -> str:
    if "." not in entity_id:
        raise HomeDeviceRegistryError("invalid primary entity")
    return entity_id.split(".", 1)[0]


def install_home_control_tools(
    core_module: Any,
    *,
    client: HomeAssistantClient | None,
    registry: HomeDeviceRegistry | None,
    emit_warnings: bool = True,
) -> bool:
    """Install write tools only when HA client + logical registry are both available.

    Every tool is registered in CONFIRM_GATED before it becomes visible to the model.
    """
    if client is None or registry is None:
        if emit_warnings:
            print("WARNING Friday home control: HA client/device registry unavailable; write tools disabled")
        return False

    def _resolve(device_alias: str, capability: str):
        device = registry.require_capability(device_alias, capability)
        return device, device.primary_entity_id

    def home_device_power(args=""):
        try:
            data = _parse(args)
            device_alias = str(data.get("device") or "").strip()
            action = str(data.get("action") or "").strip().lower()
            if action not in {"on", "off"}:
                return "คำสั่งเปิดปิดอุปกรณ์ต้องเป็น on หรือ off ค่ะ"
            device, entity_id = _resolve(device_alias, "power")
            domain = _entity_domain(entity_id)
            client.call_service(domain, "turn_on" if action == "on" else "turn_off", {"entity_id": entity_id})
            return f"{'เปิด' if action == 'on' else 'ปิด'} {device.id} ให้แล้วค่ะ"
        except (ValueError, HomeDeviceRegistryError, HomeAssistantError) as exc:
            return f"สั่งเปิดปิดอุปกรณ์ไม่สำเร็จค่ะ ({exc})"

    def home_ac_set_temperature(args=""):
        try:
            data = _parse(args)
            device_alias = str(data.get("device") or "").strip()
            temperature = float(data.get("temperature"))
            if temperature < 16 or temperature > 30:
                return "อุณหภูมิแอร์ต้องอยู่ระหว่าง 16 ถึง 30 องศาค่ะ"
            device, entity_id = _resolve(device_alias, "temperature")
            if _entity_domain(entity_id) != "climate":
                raise HomeDeviceRegistryError("temperature capability requires a climate entity")
            client.call_service(
                "climate",
                "set_temperature",
                {"entity_id": entity_id, "temperature": temperature},
            )
            display = int(temperature) if temperature.is_integer() else temperature
            return f"ตั้ง {device.id} เป็น {display} องศาแล้วค่ะ"
        except (TypeError, ValueError, HomeDeviceRegistryError, HomeAssistantError) as exc:
            if isinstance(exc, ValueError) and str(exc) == "invalid tool arguments":
                return f"ตั้งอุณหภูมิแอร์ไม่สำเร็จค่ะ ({exc})"
            if isinstance(exc, (TypeError, ValueError)):
                return "อุณหภูมิแอร์ไม่ถูกต้องค่ะ"
            return f"ตั้งอุณหภูมิแอร์ไม่สำเร็จค่ะ ({exc})"

    def home_ac_set_mode(args=""):
        try:
            data = _parse(args)
            device_alias = str(data.get("device") or "").strip()
            mode = str(data.get("mode") or "").strip().lower()
            if mode not in _ALLOWED_HVAC_MODES:
                return "โหมดแอร์ไม่อยู่ในรายการที่รองรับค่ะ"
            device, entity_id = _resolve(device_alias, "mode")
            if _entity_domain(entity_id) != "climate":
                raise HomeDeviceRegistryError("mode capability requires a climate entity")
            client.call_service("climate", "set_hvac_mode", {"entity_id": entity_id, "hvac_mode": mode})
            return f"ตั้งโหมด {device.id} เป็น {mode} แล้วค่ะ"
        except (ValueError, HomeDeviceRegistryError, HomeAssistantError) as exc:
            return f"ตั้งโหมดแอร์ไม่สำเร็จค่ะ ({exc})"

    def home_ac_set_fan_mode(args=""):
        try:
            data = _parse(args)
            device_alias = str(data.get("device") or "").strip()
            fan_mode = str(data.get("fan_mode") or "").strip().lower()
            if fan_mode not in _ALLOWED_FAN_MODES:
                return "โหมดพัดลมแอร์ไม่อยู่ในรายการที่รองรับค่ะ"
            device, entity_id = _resolve(device_alias, "fan")
            if _entity_domain(entity_id) != "climate":
                raise HomeDeviceRegistryError("fan capability requires a climate entity")
            client.call_service("climate", "set_fan_mode", {"entity_id": entity_id, "fan_mode": fan_mode})
            return f"ตั้งพัดลม {device.id} เป็น {fan_mode} แล้วค่ะ"
        except (ValueError, HomeDeviceRegistryError, HomeAssistantError) as exc:
            return f"ตั้งพัดลมแอร์ไม่สำเร็จค่ะ ({exc})"

    functions = {
        "home_device_power": home_device_power,
        "home_ac_set_temperature": home_ac_set_temperature,
        "home_ac_set_mode": home_ac_set_mode,
        "home_ac_set_fan_mode": home_ac_set_fan_mode,
    }
    core_module.TOOLS.update(functions)

    schemas = [
        {
            "type": "function",
            "function": {
                "name": "home_device_power",
                "description": "เปิดหรือปิดอุปกรณ์ในบ้านด้วย logical device alias",
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
                "description": "ตั้งอุณหภูมิแอร์ในบ้าน 16-30 องศาเซลเซียส",
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
                "name": "home_ac_set_mode",
                "description": "ตั้ง HVAC mode ของแอร์",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string"},
                        "mode": {"type": "string", "enum": sorted(_ALLOWED_HVAC_MODES)},
                    },
                    "required": ["device", "mode"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "home_ac_set_fan_mode",
                "description": "ตั้ง fan mode ของแอร์",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string"},
                        "fan_mode": {"type": "string", "enum": sorted(_ALLOWED_FAN_MODES)},
                    },
                    "required": ["device", "fan_mode"],
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
        if name in HOME_WRITE_TOOL_NAMES:
            return json.dumps(args, ensure_ascii=False, sort_keys=True)
        return legacy_pack_args(name, args)

    core_module._pack_args = _pack_args

    def _question(label: str, args: str) -> str:
        try:
            data = _parse(args)
        except ValueError:
            return f"ต้องการ{label}นะคะ ยืนยันไหมคะ"
        device = data.get("device") or "อุปกรณ์"
        if label == "เปิดปิดอุปกรณ์":
            action = "เปิด" if data.get("action") == "on" else "ปิด"
            return f"ต้องการ{action} {device} นะคะ ยืนยันไหมคะ"
        if label == "ตั้งอุณหภูมิแอร์":
            return f"ต้องการตั้ง {device} เป็น {data.get('temperature')} องศานะคะ ยืนยันไหมคะ"
        if label == "ตั้งโหมดแอร์":
            return f"ต้องการตั้ง {device} เป็นโหมด {data.get('mode')} นะคะ ยืนยันไหมคะ"
        return f"ต้องการตั้งพัดลม {device} เป็น {data.get('fan_mode')} นะคะ ยืนยันไหมคะ"

    gates = {
        "home_device_power": {
            "question": lambda args: _question("เปิดปิดอุปกรณ์", args),
            "cancel": lambda _args: "ยกเลิกการเปิดปิดอุปกรณ์แล้วค่ะ",
            "execute": home_device_power,
        },
        "home_ac_set_temperature": {
            "question": lambda args: _question("ตั้งอุณหภูมิแอร์", args),
            "cancel": lambda _args: "ยกเลิกการตั้งอุณหภูมิแอร์แล้วค่ะ",
            "execute": home_ac_set_temperature,
        },
        "home_ac_set_mode": {
            "question": lambda args: _question("ตั้งโหมดแอร์", args),
            "cancel": lambda _args: "ยกเลิกการตั้งโหมดแอร์แล้วค่ะ",
            "execute": home_ac_set_mode,
        },
        "home_ac_set_fan_mode": {
            "question": lambda args: _question("ตั้งพัดลมแอร์", args),
            "cancel": lambda _args: "ยกเลิกการตั้งพัดลมแอร์แล้วค่ะ",
            "execute": home_ac_set_fan_mode,
        },
    }
    core_module.CONFIRM_GATED.update(gates)

    if emit_warnings:
        print(f"Friday confirm-gated home write tools enabled: {len(HOME_WRITE_TOOL_NAMES)}")
    return True
