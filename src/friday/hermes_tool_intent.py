from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Iterable

from friday.home_control_runtime import HOME_WRITE_TOOL_NAMES


class HermesToolIntentError(RuntimeError):
    pass


HOME_TOOL_INTENT_ALLOWLIST = frozenset({"home_device_status", *HOME_WRITE_TOOL_NAMES})
_CORRELATION_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_MAX_ARGUMENT_BYTES = 4096


@dataclass(frozen=True)
class ValidatedToolIntent:
    correlation_id: str
    tool_name: str
    arguments: dict[str, Any]
    packed_args: str
    requires_confirmation: bool


def _tool_schema_map(core_module: Any) -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for wrapper in core_module.TOOL_SCHEMAS:
        if not isinstance(wrapper, dict):
            continue
        fn = wrapper.get("function")
        if isinstance(fn, dict) and isinstance(fn.get("name"), str):
            schemas[fn["name"]] = fn
    return schemas


def _validate_value(name: str, value: Any, schema: dict[str, Any]) -> None:
    expected = schema.get("type")
    if expected == "string":
        if not isinstance(value, str):
            raise HermesToolIntentError(f"argument {name} must be string")
        if len(value) > 256:
            raise HermesToolIntentError(f"argument {name} is too long")
    elif expected == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise HermesToolIntentError(f"argument {name} must be number")
    elif expected == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise HermesToolIntentError(f"argument {name} must be integer")
    elif expected == "boolean":
        if not isinstance(value, bool):
            raise HermesToolIntentError(f"argument {name} must be boolean")

    if "enum" in schema and value not in schema["enum"]:
        raise HermesToolIntentError(f"argument {name} is not in the allowed enum")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            raise HermesToolIntentError(f"argument {name} is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise HermesToolIntentError(f"argument {name} is above maximum")


def _validate_arguments(arguments: dict[str, Any], function_schema: dict[str, Any]) -> None:
    parameters = function_schema.get("parameters") or {}
    if parameters.get("type") not in {None, "object"}:
        raise HermesToolIntentError("unsupported tool parameter schema")
    properties = parameters.get("properties") or {}
    required = set(parameters.get("required") or [])
    if not isinstance(properties, dict):
        raise HermesToolIntentError("invalid tool parameter schema")

    missing = sorted(name for name in required if name not in arguments)
    if missing:
        raise HermesToolIntentError("missing required arguments: " + ", ".join(missing))

    unknown = sorted(name for name in arguments if name not in properties)
    if unknown:
        raise HermesToolIntentError("unknown arguments: " + ", ".join(unknown))

    for name, value in arguments.items():
        property_schema = properties.get(name)
        if not isinstance(property_schema, dict):
            raise HermesToolIntentError(f"invalid schema for argument {name}")
        _validate_value(name, value, property_schema)


def validate_hermes_tool_intent(
    payload: dict[str, Any],
    core_module: Any,
    *,
    allowed_tools: Iterable[str] = HOME_TOOL_INTENT_ALLOWLIST,
) -> ValidatedToolIntent:
    """Validate only. This function never executes a Friday tool.

    Friday, not Hermes, determines confirmation requirements from the live `CONFIRM_GATED`
    registry. Hermes is not allowed to assert or override safety policy in the payload.
    """
    if not isinstance(payload, dict):
        raise HermesToolIntentError("tool intent must be an object")
    if payload.get("type") != "tool_intent" or payload.get("version") != 1:
        raise HermesToolIntentError("unsupported tool intent envelope")

    allowed_envelope_fields = {"type", "version", "correlation_id", "tool", "arguments"}
    unknown_fields = sorted(key for key in payload if key not in allowed_envelope_fields)
    if unknown_fields:
        raise HermesToolIntentError("unknown tool intent fields: " + ", ".join(unknown_fields))

    correlation_id = str(payload.get("correlation_id") or "").strip()
    if not _CORRELATION_ID_RE.fullmatch(correlation_id):
        raise HermesToolIntentError("invalid correlation_id")

    tool_name = str(payload.get("tool") or "").strip()
    allowed = frozenset(allowed_tools)
    if tool_name not in allowed:
        raise HermesToolIntentError("tool is not allowed for Hermes home intent")
    if tool_name not in core_module.TOOLS:
        raise HermesToolIntentError("tool is not registered in Friday")

    arguments = payload.get("arguments")
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise HermesToolIntentError("arguments must be an object")
    encoded = json.dumps(arguments, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > _MAX_ARGUMENT_BYTES:
        raise HermesToolIntentError("arguments are too large")

    schemas = _tool_schema_map(core_module)
    function_schema = schemas.get(tool_name)
    if function_schema is None:
        raise HermesToolIntentError("tool schema is not registered in Friday")
    _validate_arguments(arguments, function_schema)

    requires_confirmation = tool_name in core_module.CONFIRM_GATED
    if tool_name in HOME_WRITE_TOOL_NAMES and not requires_confirmation:
        raise HermesToolIntentError("home write tool is missing Friday confirmation gate")

    packed_args = core_module._pack_args(tool_name, arguments)
    if not isinstance(packed_args, str):
        raise HermesToolIntentError("Friday argument packer returned invalid data")

    return ValidatedToolIntent(
        correlation_id=correlation_id,
        tool_name=tool_name,
        arguments=dict(arguments),
        packed_args=packed_args,
        requires_confirmation=requires_confirmation,
    )
