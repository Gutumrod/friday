"""Guarded ASGI entrypoint for the Friday API service."""
from friday import core
from friday.home_assistant_runtime import install_home_assistant_read_tools
from friday.runtime_security import apply_runtime_security

apply_runtime_security(core)
install_home_assistant_read_tools(core)

from friday.api import app  # noqa: E402

__all__ = ["app"]
