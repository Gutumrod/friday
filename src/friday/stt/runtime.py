from __future__ import annotations

from typing import Any

from friday.stt.base import STTProvider
from friday.stt.factory import create_stt_provider, provider_warnings


def install_stt_provider(
    core_module: Any,
    *,
    provider: STTProvider | None = None,
    emit_warnings: bool = True,
) -> STTProvider:
    """Install a provider behind core._recognize_speech without changing the voice loop.

    The legacy function stays in core.py as a rollback path until Phase 1 is live-verified on
    the Windows Friday machine. Production launchers call this before core.main().
    """
    provider = provider or create_stt_provider()

    def _recognize_with_provider(recognizer: Any, audio: Any):
        result = provider.transcribe(recognizer, audio)
        core_module._latency.record(
            "stt_provider_result",
            provider=result.provider,
            latency_ms=result.latency_ms,
            recognized=bool(result.text),
            unclear=result.unclear,
            fallback_used=result.fallback_used,
            metadata=result.metadata,
        )
        if result.text:
            suffix = " (fallback)" if result.fallback_used else ""
            print(f"👤 คุณพูดว่า{suffix}: {result.text}")
            return result.text
        if result.unclear:
            print("👩‍💼 Friday: ขอโทษค่ะ ฉันฟังไม่ชัด ลองพูดใหม่อีกทีนะคะ")
            return None
        return None

    core_module._recognize_speech = _recognize_with_provider
    core_module.FRIDAY_STT_PROVIDER_NAME = provider.name

    if emit_warnings:
        for warning in provider_warnings(provider.name):
            print(f"WARNING Friday STT: {warning}")
        print(f"Friday STT provider: {provider.name}")
    return provider
