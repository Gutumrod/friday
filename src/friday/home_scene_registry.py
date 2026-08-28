from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from friday.config import PROJECT_DIR
from friday.home_device_registry import normalize_device_alias


class HomeSceneRegistryError(RuntimeError):
    pass


class UnknownHomeScene(HomeSceneRegistryError):
    pass


@dataclass(frozen=True)
class HomeScene:
    id: str
    aliases: tuple[str, ...]
    entity_id: str
    description: str = ""


class HomeSceneRegistry:
    def __init__(self, scenes: list[HomeScene]) -> None:
        if not scenes:
            raise HomeSceneRegistryError("scene registry is empty")
        self._scenes = {scene.id: scene for scene in scenes}
        if len(self._scenes) != len(scenes):
            raise HomeSceneRegistryError("duplicate scene id")
        aliases: dict[str, str] = {}
        for scene in scenes:
            if not scene.entity_id.startswith("scene."):
                raise HomeSceneRegistryError(f"scene {scene.id} must map to a scene.* entity")
            for raw_alias in (scene.id, *scene.aliases):
                normalized = normalize_device_alias(raw_alias)
                if not normalized:
                    raise HomeSceneRegistryError(f"scene {scene.id} has an empty alias")
                existing = aliases.get(normalized)
                if existing and existing != scene.id:
                    raise HomeSceneRegistryError(
                        f"ambiguous scene alias {raw_alias!r} maps to both {existing} and {scene.id}"
                    )
                aliases[normalized] = scene.id
        self._aliases = aliases

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HomeSceneRegistry":
        if payload.get("version") != 1:
            raise HomeSceneRegistryError("unsupported scene registry version")
        rows = payload.get("scenes")
        if not isinstance(rows, list):
            raise HomeSceneRegistryError("scene registry scenes must be a list")
        scenes: list[HomeScene] = []
        for row in rows:
            if not isinstance(row, dict):
                raise HomeSceneRegistryError("scene entry must be an object")
            scene_id = str(row.get("id") or "").strip()
            aliases = row.get("aliases") or []
            entity_id = str(row.get("entity_id") or "").strip()
            description = str(row.get("description") or "").strip()
            if not scene_id or not entity_id:
                raise HomeSceneRegistryError("scene id and entity_id are required")
            if not isinstance(aliases, list) or not all(isinstance(alias, str) for alias in aliases):
                raise HomeSceneRegistryError(f"scene {scene_id} aliases must be strings")
            scenes.append(HomeScene(scene_id, tuple(aliases), entity_id, description))
        return cls(scenes)

    @classmethod
    def from_file(cls, path: str | os.PathLike[str]) -> "HomeSceneRegistry":
        file_path = Path(path)
        try:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise HomeSceneRegistryError(f"scene registry not found: {file_path}") from exc
        except json.JSONDecodeError as exc:
            raise HomeSceneRegistryError("scene registry is invalid JSON") from exc
        if not isinstance(payload, dict):
            raise HomeSceneRegistryError("scene registry root must be an object")
        return cls.from_dict(payload)

    @classmethod
    def from_env(cls) -> "HomeSceneRegistry":
        configured = os.environ.get("HOME_SCENE_REGISTRY_PATH", "").strip()
        path = configured or os.path.join(PROJECT_DIR, "home_scenes.json")
        return cls.from_file(path)

    def resolve(self, alias_or_id: str) -> HomeScene:
        scene_id = self._aliases.get(normalize_device_alias(alias_or_id))
        if not scene_id:
            raise UnknownHomeScene(f"unknown home scene: {alias_or_id}")
        return self._scenes[scene_id]

    def list_scenes(self) -> list[HomeScene]:
        return list(self._scenes.values())
