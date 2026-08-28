"""Phase 9 remote-command policy checks. No network listener is opened."""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday.remote_command_policy import (
    CommandContext,
    CommandSource,
    ConfirmationProof,
    RemoteCommandPolicyError,
    audit_record,
    authorize_confirmed_execution,
    evaluate_tool_request,
)


def core():
    power = lambda args: "power"
    return SimpleNamespace(
        TOOLS={"home_device_status": lambda args: "status", "home_device_power": power},
        CONFIRM_GATED={"home_device_power": {"execute": power}},
    )


def expect_error(fn, contains):
    try:
        fn()
    except RemoteCommandPolicyError as exc:
        assert contains in str(exc), str(exc)
        return
    raise AssertionError("expected RemoteCommandPolicyError")


def remote(request_id="req_1", subject="owner@example", authenticated=True):
    return CommandContext(CommandSource.REMOTE_API, request_id, authenticated, subject)


def check_unauthenticated_remote_rejected():
    expect_error(lambda: evaluate_tool_request(core(), "home_device_status", remote(authenticated=False)), "not authenticated")


def check_remote_read_can_stage_without_confirm():
    decision = evaluate_tool_request(core(), "home_device_status", remote())
    assert decision.allowed_to_stage is True
    assert decision.requires_confirmation is False
    assert decision.audit_required is True


def check_remote_write_stages_but_requires_confirm():
    decision = evaluate_tool_request(core(), "home_device_power", remote())
    assert decision.allowed_to_stage is True
    assert decision.requires_confirmation is True
    assert decision.audit_required is True


def check_remote_write_without_proof_cannot_execute():
    expect_error(
        lambda: authorize_confirmed_execution(core(), "home_device_power", remote(), None),
        "confirmation proof required",
    )


def check_confirmation_must_bind_request_and_subject():
    context = remote(request_id="req_123", subject="owner@example")
    expect_error(
        lambda: authorize_confirmed_execution(
            core(),
            "home_device_power",
            context,
            ConfirmationProof("confirm_1", "wrong_request", "owner@example"),
        ),
        "request_id mismatch",
    )
    expect_error(
        lambda: authorize_confirmed_execution(
            core(),
            "home_device_power",
            context,
            ConfirmationProof("confirm_1", "req_123", "attacker@example"),
        ),
        "subject mismatch",
    )


def check_valid_remote_confirmation_authorizes():
    context = remote(request_id="req_123", subject="owner@example")
    proof = ConfirmationProof("confirm_1", "req_123", "owner@example")
    assert authorize_confirmed_execution(core(), "home_device_power", context, proof) is True


def check_remote_read_needs_no_confirmation_proof():
    assert authorize_confirmed_execution(core(), "home_device_status", remote(), None) is True


def check_audit_excludes_arguments_and_tokens():
    context = remote(request_id="req_123", subject="owner@example")
    record = audit_record(tool_name="home_device_power", context=context, outcome="staged", confirmed=False)
    assert record == {
        "request_id": "req_123",
        "source": "remote_api",
        "subject": "owner@example",
        "tool": "home_device_power",
        "outcome": "staged",
        "confirmed": False,
    }
    assert "arguments" not in record and "token" not in record


TESTS = [
    check_unauthenticated_remote_rejected,
    check_remote_read_can_stage_without_confirm,
    check_remote_write_stages_but_requires_confirm,
    check_remote_write_without_proof_cannot_execute,
    check_confirmation_must_bind_request_and_subject,
    check_valid_remote_confirmation_authorizes,
    check_remote_read_needs_no_confirmation_proof,
    check_audit_excludes_arguments_and_tokens,
]


if __name__ == "__main__":
    failures = []
    for test in TESTS:
        try:
            test()
            print(f"[PASS] {test.__name__}")
        except Exception as exc:
            failures.append((test.__name__, exc))
            print(f"[FAIL] {test.__name__}: {type(exc).__name__}: {exc}")
    if failures:
        raise SystemExit(1)
    print(f"Phase 9 remote policy checks passed: {len(TESTS)}/{len(TESTS)}")
