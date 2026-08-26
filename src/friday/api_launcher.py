"""Guarded ASGI entrypoint for the Friday API service."""
from friday import core
from friday.home_assistant_runtime import install_home_assistant_read_tools
from friday.home_control_runtime import install_home_control_tools
from friday.home_device_runtime import install_home_device_read_tools
from friday.home_scene_runtime import install_home_scene_tools
from friday.runtime_security import apply_runtime_security

apply_runtime_security(core)
ha_client = install_home_assistant_read_tools(core)
home_registry = install_home_device_read_tools(core, client=ha_client)
install_home_control_tools(core, client=ha_client, registry=home_registry)
install_home_scene_tools(core, client=ha_client)

from friday.api import app  # noqa: E402

__all__ = ["app"]
