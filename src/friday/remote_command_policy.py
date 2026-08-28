from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class RemoteCommandPolicyError(RuntimeError):
    pass


class CommandSource(str, Enum):
    LOCAL_VOICE = "local_voice"
    LOCAL_API = "local_api"
    REMOTE_API = "remote_api"


_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_SUBJECT_RE = re.compile(r"^[A-Za-z0-9_.:@-]{1,128}$")


@dataclass(frozen=True)
class CommandContext:
    source: CommandSource
    request_id: str
    authenticated: bool = False
    subject: str = ""

    def validate(self) -> None:
        if not _REQUEST_ID_RE.fullmatch(self.request_id):
            raise RemoteCommandPolicyError("invalid request_id")
        if self.source == CommandSource.REMOTE_API:
            if not self.authenticated:
                raise RemoteCommandPolicyError("remote request is not authenticated")
            if not _SUBJECT_RE.fullmatch(self.subject):
                raise RemoteCommandPolicyError("remote authenticated subject is invalid")
        elif self.subject and not _SUBJECT_RE.fullmatch(self.subject):
            raise RemoteCommandPolicyError("authenticated subject is invalid")


@dataclass(frozen=True)
class CommandPolicyDecision:
    allowed_to_stage: bool
    requires_confirmation: bool
    audit_required: bool
    reason: str


@dataclass(frozen=True)
class ConfirmationProof:
    confirmation_id: str
    request_id: str
    subject: str

    def validate_for(self, context: CommandContext) -> None:
        if not self.confirmation_id or len(self.confirmation_id) > 128:
            raise RemoteCommandPolicyError("invalid confirmation_id")
        if self.request_id != context.request_id:
            raise RemoteCommandPolicyError("confirmation request_id mismatch")
        if context.source == CommandSource.REMOTE_API and self.subject != context.subject:
            raise RemoteCommandPolicyError("confirmation subject mismatch")


def evaluate_tool_request(core_module: Any, tool_name: str, context: CommandContext) -> CommandPolicyDecision:
    """Decide whether a request may enter Friday's normal tool/confirm flow.

    This never executes a tool and never weakens `CONFIRM_GATED`. Remote side effects are only
    allowed to be *staged* for a separate confirmation step.
    """
    context.validate()
    tool_name = tool_name.strip()
    if not tool_name or tool_name not in core_module.TOOLS:
        raise RemoteCommandPolicyError("tool is not registered in Friday")

    requires_confirmation = tool_name in core_module.CONFIRM_GATED
    if context.source == CommandSource.REMOTE_API:
        return CommandPolicyDecision(
            allowed_to_stage=True,
            requires_confirmation=requires_confirmation,
            audit_required=True,
            reason="authenticated remote request",
        )

    return CommandPolicyDecision(
        allowed_to_stage=True,
        requires_confirmation=requires_confirmation,
        audit_required=requires_confirmation,
        reason="local request",
    )


def authorize_confirmed_execution(
    core_module: Any,
    tool_name: str,
    context: CommandContext,
    proof: ConfirmationProof | None,
) -> bool:
    """Check execution authorization after a confirmation flow has completed.

    A remote side-effect cannot be executed from a one-shot `confirm=true` flag in the original
    request. It requires a separate confirmation proof bound to request ID + authenticated subject.
    """
    decision = evaluate_tool_request(core_module, tool_name, context)
    if not decision.requires_confirmation:
        return True
    if proof is None:
        raise RemoteCommandPolicyError("confirmation proof required")
    proof.validate_for(context)
    return True


def audit_record(
    *,
    tool_name: str,
    context: CommandContext,
    outcome: str,
    confirmed: bool,
) -> dict[str, Any]:
    """Build a minimal audit record. Arguments/tokens are intentionally excluded."""
    context.validate()
    if outcome not in {"staged", "confirmed", "cancelled", "rejected", "executed", "error"}:
        raise RemoteCommandPolicyError("invalid audit outcome")
    return {
        "request_id": context.request_id,
        "source": context.source.value,
        "subject": context.subject if context.authenticated else "",
        "tool": tool_name,
        "outcome": outcome,
        "confirmed": bool(confirmed),
    }
