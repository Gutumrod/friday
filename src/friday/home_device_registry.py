from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from friday.config import PROJECT_DIR


class HomeDeviceRegistryError(RuntimeError):
    pass


class UnknownHomeDevice(HomeDeviceRegistryError):
    pass


class UnsupportedCapability(HomeDeviceRegistryError):
    pass


_ALIAS_SEP_RE = re.compile(r"[\s_-]+", re.UNICODE)
_ALIAS_CLEAN_RE = re.compile(r"[^\w\u0E00-\u0E7F]+", re.UNICODE)


def normalize_device_alias(value: str) -> str:
    compact = _ALIAS_SEP_RE.sub(" ", value.strip().lower())
    return _ALIAS_CLEAN_RE.sub("", compact)


@dataclass(frozen=True)
class HomeDevice:
    id: str
    aliases: tuple[str, ...]
    entities: dict[str, str]
    capabilities: frozenset[str]
    room: str = ""

    @property
    def primary_entity_id(self) -> str:
        entity_id = self.entities.get("primary", "").strip()
        if not entity_id:
            raise HomeDeviceRegistryError(f"device {self.id} has no primary entity")
        return entity_id


class HomeDeviceRegistry:
    def __init__(self, devices: list[HomeDevice]) -> None:
        if not devices:
            raise HomeDeviceRegistryError("device registry is empty")
        self._devices = {device.id: device for device in devices}
        if len(self._devices) != len(devices):
            raise HomeDeviceRegistryError("duplicate device id")

        aliases: dict[str, str] = {}
        for device in devices:
            candidates = [device.id, *device.aliases]
            for raw_alias in candidates:
                normalized = normalize_device_alias(raw_alias)
                if not normalized:
                    raise HomeDeviceRegistryError(f"device {device.id} has an empty alias")
                existing = aliases.get(normalized)
                if existing and existing != device.id:
                    raise HomeDeviceRegistryError(
                        f"ambiguous alias {raw_alias!r} maps to both {existing} and {device.id}"
                    )
                aliases[normalized] = device.id
        self._aliases = aliases

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HomeDeviceRegistry":
        if payload.get("version") != 1:
            raise HomeDeviceRegistryError("unsupported device registry version")
        raw_devices = payload.get("devices")
        if not isinstance(raw_devices, list):
            raise HomeDeviceRegistryError("device registry devices must be a list")
        devices: list[HomeDevice] = []
        for row in raw_devices:
            if not isinstance(row, dict):
                raise HomeDeviceRegistryError("device entry must be an object")
            device_id = str(row.get("id") or "").strip()
            aliases = row.get("aliases") or []
            entities = row.get("entities") or {}
            capabilities = row.get("capabilities") or []
            if not device_id:
                raise HomeDeviceRegistryError("device id is required")
            if not isinstance(aliases, list) or not all(isinstance(v, str) for v in aliases):
                raise HomeDeviceRegistryError(f"device {device_id} aliases must be strings")
            if not isinstance(entities, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in entities.items()):
                raise HomeDeviceRegistryError(f"device {device_id} entities must be string mappings")
            if not isinstance(capabilities, list) or not all(isinstance(v, str) for v in capabilities):
                raise HomeDeviceRegistryError(f"device {device_id} capabilities must be strings")
            device = HomeDevice(
                id=device_id,
                aliases=tuple(aliases),
                entities={k.strip(): v.strip() for k, v in entities.items()},
                capabilities=frozenset(v.strip().lower() for v in capabilities if v.strip()),
                room=str(row.get("room") or "").strip(),
            )
            _ = device.primary_entity_id
            devices.append(device)
        return cls(devices)

    @classmethod
    def from_file(cls, path: str | os.PathLike[str]) -> "HomeDeviceRegistry":
        file_path = Path(path)
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise HomeDeviceRegistryError(f"device registry not found: {file_path}") from exc
        except json.JSONDecodeError as exc:
            raise HomeDeviceRegistryError("device registry is invalid JSON") from exc
        if not isinstance(payload, dict):
            raise HomeDeviceRegistryError("device registry root must be an object")
        return cls.from_dict(payload)

    @classmethod
    def from_env(cls) -> "HomeDeviceRegistry":
        configured = os.environ.get("HOME_DEVICE_REGISTRY_PATH", "").strip()
        path = configured or os.path.join(PROJECT_DIR, "home_devices.json")
        return cls.from_file(path)

    def resolve(self, alias_or_id: str) -> HomeDevice:
        normalized = normalize_device_alias(alias_or_id)
        device_id = self._aliases.get(normalized)
        if not device_id:
            raise UnknownHomeDevice(f"unknown home device: {alias_or_id}")
        return self._devices[device_id]

    def require_capability(self, alias_or_id: str, capability: str) -> HomeDevice:
        device = self.resolve(alias_or_id)
        normalized = capability.strip().lower()
        if normalized not in device.capabilities:
            raise UnsupportedCapability(f"device {device.id} does not support {normalized}")
        return device

    def allowed_entity_ids(self) -> set[str]:
        return {entity_id for device in self._devices.values() for entity_id in device.entities.values() if entity_id}

    def list_devices(self) -> list[HomeDevice]:
        return list(self._devices.values())
