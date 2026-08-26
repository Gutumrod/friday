"""Phase 0 security/config regression checks.

Stdlib-only on purpose: this can run without loading Friday's audio/vision dependencies.
Run from repository root with: python src/test_phase0_security.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday import config
from friday import runtime_security


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def test_source_has_no_tv_secret_default():
    path = os.path.join(ROOT, "src", "friday", "config.py")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    check('TV_CLIENT_KEY = _env_str("FRIDAY_TV_CLIENT_KEY")' in source, "TV client key must come from env")
    check('TV_CLIENT_KEY = "' not in source, "TV client key must not have a quoted source default")
    check('GOOGLE_CLOUD_CREDS_PATH = _env_str("GOOGLE_CLOUD_CREDS_PATH")' in source, "GCP credential path must be machine-local")


def test_env_file_is_ignored_and_example_is_placeholder_only():
    with open(os.path.join(ROOT, ".gitignore"), "r", encoding="utf-8") as f:
        ignored = {line.strip() for line in f if line.strip() and not line.startswith("#")}
    check(".env" in ignored, ".env must stay gitignored")

    with open(os.path.join(ROOT, ".env.example"), "r", encoding="utf-8") as f:
        example = f.read()
    check("FRIDAY_TV_CLIENT_KEY=replace_after_pairing" in example, ".env.example must contain only a placeholder client key")


def test_tv_config_diagnostics_never_echo_secret_values():
    names = ("TV_IP", "TV_MAC", "TV_CLIENT_KEY", "TV_BROADCAST_IP")
    original = {name: getattr(config, name) for name in names}
    secret_marker = "DO_NOT_ECHO_THIS_SECRET_7f3e"
    try:
        config.TV_IP = ""
        config.TV_MAC = ""
        config.TV_CLIENT_KEY = secret_marker
        config.TV_BROADCAST_IP = ""
        rendered = "\n".join(config.tv_config_issues())
        check(secret_marker not in rendered, "config diagnostics leaked a secret value")
        check("FRIDAY_TV_IP" in rendered and "FRIDAY_TV_MAC" in rendered, "missing variables should be named safely")
    finally:
        for name, value in original.items():
            setattr(config, name, value)


def test_runtime_guard_disables_tv_side_effects_when_config_is_invalid():
    names = ("TV_IP", "TV_MAC", "TV_CLIENT_KEY", "TV_BROADCAST_IP")
    original = {name: getattr(config, name) for name in names}

    def should_never_run(_args=""):
        raise AssertionError("unguarded TV side effect executed")

    class FakeCore:
        TOOLS = {name: should_never_run for name in runtime_security.TV_TOOL_NAMES}
        CONFIRM_GATED = {
            name: {
                "question": lambda _args: "confirm",
                "cancel": lambda _args: "cancel",
                "execute": should_never_run,
            }
            for name in runtime_security.TV_TOOL_NAMES
        }

    try:
        config.TV_IP = ""
        config.TV_MAC = ""
        config.TV_CLIENT_KEY = ""
        config.TV_BROADCAST_IP = ""
        warnings = runtime_security.apply_runtime_security(FakeCore, emit_warnings=False)
        check(warnings, "invalid machine config should produce a startup warning")
        for name in runtime_security.TV_TOOL_NAMES:
            output = FakeCore.TOOLS[name]("")
            check("ยังไม่ได้ตั้งค่า LG TV" in output, f"{name} did not fail closed")
            gated_output = FakeCore.CONFIRM_GATED[name]["execute"]("")
            check("ยังไม่ได้ตั้งค่า LG TV" in gated_output, f"{name} confirm executor did not fail closed")
    finally:
        for name, value in original.items():
            setattr(config, name, value)


def test_valid_tv_config_does_not_replace_tools():
    names = ("TV_IP", "TV_MAC", "TV_CLIENT_KEY", "TV_BROADCAST_IP")
    original = {name: getattr(config, name) for name in names}

    def original_tool(_args=""):
        return "original"

    class FakeCore:
        TOOLS = {name: original_tool for name in runtime_security.TV_TOOL_NAMES}
        CONFIRM_GATED = {
            name: {
                "question": lambda _args: "confirm",
                "cancel": lambda _args: "cancel",
                "execute": original_tool,
            }
            for name in runtime_security.TV_TOOL_NAMES
        }

    try:
        config.TV_IP = "192.0.2.10"
        config.TV_MAC = "00:11:22:33:44:55"
        config.TV_CLIENT_KEY = "paired-key-placeholder"
        config.TV_BROADCAST_IP = "192.0.2.255"
        runtime_security.apply_runtime_security(FakeCore, emit_warnings=False)
        for name in runtime_security.TV_TOOL_NAMES:
            check(FakeCore.TOOLS[name] is original_tool, f"{name} was replaced despite valid config")
            check(FakeCore.CONFIRM_GATED[name]["execute"] is original_tool, f"{name} gate was replaced despite valid config")
    finally:
        for name, value in original.items():
            setattr(config, name, value)


def main():
    tests = [
        test_source_has_no_tv_secret_default,
        test_env_file_is_ignored_and_example_is_placeholder_only,
        test_tv_config_diagnostics_never_echo_secret_values,
        test_runtime_guard_disables_tv_side_effects_when_config_is_invalid,
        test_valid_tv_config_does_not_replace_tools,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS Phase 0 security checks: {len(tests)}/{len(tests)}")


if __name__ == "__main__":
    main()
