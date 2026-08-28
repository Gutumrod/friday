"""Runtime safety guards for optional machine-local integrations.

This module deliberately has no dependency on Friday's heavy audio/vision runtime so its
configuration behavior can be tested without loading pygame, cv2, or device drivers.
"""
from __future__ import annotations

from typing import Any

from friday import config as _config

TV_TOOL_NAMES = (
    "tv_power",
    "tv_volume",
    "tv_launch_app",
    "tv_play_video",
    "tv_remote_button",
)


def _tv_unavailable(_args=""):
    return "ยังไม่ได้ตั้งค่า LG TV ใน .env ให้ครบค่ะ เลยยังสั่งทีวีไม่ได้"


def apply_runtime_security(core_module: Any, *, emit_warnings: bool = True) -> list[str]:
    """Apply fail-closed guards for supported entrypoints and return safe startup warnings."""
    warnings = _config.runtime_config_warnings()
    tv_issues = _config.tv_config_issues()

    if tv_issues:
        for name in TV_TOOL_NAMES:
            if name in core_module.TOOLS:
                core_module.TOOLS[name] = _tv_unavailable
            gate = core_module.CONFIRM_GATED.get(name)
            if gate:
                gate["execute"] = _tv_unavailable

    if emit_warnings:
        for warning in warnings:
            print(f"WARNING Friday config: {warning}")
    return warnings
