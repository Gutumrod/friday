"""Read-only LAN camera discovery for Friday.

This module intentionally discovers metadata only. It never authenticates to a camera,
opens a stream, changes settings, or exposes discovery encryption material.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any


DEFAULT_DISCOVERY_TARGET = "255.255.255.255"
DEFAULT_DISCOVERY_TIMEOUT = 4.0


def _value(data: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = data.get(name)
        if value not in (None, ""):
            return value
    return None


def sanitize_discovery_result(host: str | None, payload: Any) -> dict[str, Any] | None:
    """Return only non-secret camera metadata from a python-kasa discovery payload."""
    if not isinstance(payload, dict):
        return None
    result = payload.get("result", payload)
    if not isinstance(result, dict) or result.get("device_type") != "SMART.IPCAMERA":
        return None
    management = result.get("mgt_encrypt_schm")
    https_supported = management.get("is_support_https") if isinstance(management, dict) else None
    return {
        "ip": _value(result, "ip") or host,
        "mac": _value(result, "mac"),
        "model": _value(result, "device_model", "model"),
        "name": _value(result, "device_name", "alias"),
        "device_type": "SMART.IPCAMERA",
        "firmware": _value(result, "firmware_version", "fw_ver"),
        "hardware": _value(result, "hardware_version", "hw_ver"),
        "https": https_supported,
        "iot_cloud": result.get("is_support_iot_cloud"),
    }


def _safe_device_metadata(host: str, device: Any) -> dict[str, Any] | None:
    """Best-effort metadata for camera types python-kasa supports directly."""
    dtype = str(getattr(device, "device_type", ""))
    if "camera" not in dtype.lower():
        return None
    return {
        "ip": getattr(device, "host", None) or host,
        "mac": getattr(device, "mac", None),
        "model": getattr(device, "model", None),
        "name": getattr(device, "alias", None),
        "device_type": dtype,
        "firmware": None,
        "hardware": None,
        "https": None,
        "iot_cloud": None,
    }


async def _discover_async(target: str, timeout: float) -> list[dict[str, Any]]:
    try:
        from kasa import Discover
    except ImportError as exc:
        raise RuntimeError("python-kasa is not installed") from exc

    found: dict[str, dict[str, Any]] = {}

    async def on_unsupported(exc: Any) -> None:
        item = sanitize_discovery_result(
            getattr(exc, "host", None),
            getattr(exc, "discovery_result", None),
        )
        if item and item.get("ip"):
            found[str(item["ip"])] = item

    async def on_discovered(device: Any) -> None:
        host = str(getattr(device, "host", ""))
        item = _safe_device_metadata(host, device)
        if item and item.get("ip"):
            found[str(item["ip"])] = item

    logger = logging.getLogger("kasa.discover")
    previous_level = logger.level
    logger.setLevel(logging.ERROR)
    try:
        await Discover.discover(
            target=target,
            discovery_timeout=timeout,
            discovery_packets=2,
            on_discovered=on_discovered,
            on_unsupported=on_unsupported,
        )
    finally:
        logger.setLevel(previous_level)
    return [found[ip] for ip in sorted(found)]


def discover_home_cameras(
    target: str | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    """Discover local cameras without authenticating or changing device state."""
    target = target or os.environ.get("FRIDAY_HOME_DISCOVERY_TARGET", DEFAULT_DISCOVERY_TARGET)
    timeout = timeout or float(
        os.environ.get("FRIDAY_HOME_DISCOVERY_TIMEOUT_SECONDS", str(DEFAULT_DISCOVERY_TIMEOUT))
    )
    return asyncio.run(_discover_async(target, timeout))


def format_camera_discovery(cameras: list[dict[str, Any]]) -> str:
    if not cameras:
        return "ยังไม่เจอกล้องที่รองรับการค้นหาในวงเครือข่ายตอนนี้ค่ะ"

    parts = []
    for camera in cameras:
        model = camera.get("model") or "ไม่ทราบรุ่น"
        name = camera.get("name") or "ไม่ทราบชื่อ"
        ip = camera.get("ip") or "ไม่ทราบ IP"
        firmware = camera.get("firmware")
        detail = f"{model} ชื่อ {name} ที่ {ip}"
        if firmware:
            detail += f" firmware {firmware}"
        parts.append(detail)
    return f"เจอกล้องในบ้าน {len(cameras)} ตัว: " + "; ".join(parts) + " ค่ะ"
