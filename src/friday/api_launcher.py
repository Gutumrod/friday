"""Guarded ASGI entrypoint for the Friday API service."""
from friday import core
from friday.runtime_security import apply_runtime_security

apply_runtime_security(core)

from friday.api import app  # noqa: E402

__all__ = ["app"]
