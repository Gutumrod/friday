from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class STTProviderError(RuntimeError):
    """Base error for provider failures that should count as a hard STT failure."""


class STTUnavailableError(STTProviderError):
    """Raised when an optional provider cannot be loaded on the current machine."""


@dataclass(frozen=True)
class STTResult:
    provider: str
    text: str | None
    latency_ms: float
    unclear: bool = False
    fallback_used: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class STTProvider(Protocol):
    name: str

    def transcribe(self, recognizer: Any, audio: Any) -> STTResult:
        """Return a normalized result or raise STTProviderError on a hard failure."""
        ...
