from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class StreamingSTTError(RuntimeError):
    pass


@dataclass(frozen=True)
class StreamingTranscript:
    sequence: int
    text: str
    final: bool
    latency_ms: float | None = None


class StreamingSTTEngine(Protocol):
    name: str

    def start(self, *, sample_rate_hz: int, sample_width_bytes: int, channels: int) -> None:
        ...

    def push_pcm(self, pcm: bytes) -> list[StreamingTranscript]:
        ...

    def finish(self) -> list[StreamingTranscript]:
        ...

    def reset(self) -> None:
        ...


@dataclass(frozen=True)
class StreamingAudioPolicy:
    sample_rate_hz: int = 16000
    sample_width_bytes: int = 2
    channels: int = 1
    chunk_ms: int = 160
    max_utterance_seconds: float = 20.0

    @property
    def bytes_per_chunk(self) -> int:
        frames = round(self.sample_rate_hz * (self.chunk_ms / 1000.0))
        return frames * self.sample_width_bytes * self.channels

    def validate(self) -> None:
        if self.sample_rate_hz <= 0:
            raise StreamingSTTError("sample_rate_hz must be positive")
        if self.sample_width_bytes not in {1, 2, 3, 4}:
            raise StreamingSTTError("unsupported sample width")
        if self.channels != 1:
            raise StreamingSTTError("Friday streaming STT currently requires mono audio")
        if self.chunk_ms < 20 or self.chunk_ms > 2000:
            raise StreamingSTTError("chunk_ms out of range")
        if self.max_utterance_seconds <= 0 or self.max_utterance_seconds > 120:
            raise StreamingSTTError("max_utterance_seconds out of range")


class StreamingSTTSession:
    """Small state machine around a model-specific streaming engine.

    No microphone ownership lives here. Phase 3 can test engine/session behavior independently
    before replacing Friday's stable turn-based SpeechRecognition capture loop.
    """

    def __init__(self, engine: StreamingSTTEngine, policy: StreamingAudioPolicy | None = None) -> None:
        self.engine = engine
        self.policy = policy or StreamingAudioPolicy()
        self.policy.validate()
        self._started = False
        self._finished = False
        self._bytes_received = 0

    def start(self) -> None:
        if self._started and not self._finished:
            raise StreamingSTTError("streaming session already started")
        self.engine.reset()
        self.engine.start(
            sample_rate_hz=self.policy.sample_rate_hz,
            sample_width_bytes=self.policy.sample_width_bytes,
            channels=self.policy.channels,
        )
        self._started = True
        self._finished = False
        self._bytes_received = 0

    def push_pcm(self, pcm: bytes) -> list[StreamingTranscript]:
        if not self._started or self._finished:
            raise StreamingSTTError("streaming session is not active")
        if not isinstance(pcm, (bytes, bytearray)) or not pcm:
            raise StreamingSTTError("pcm chunk must be non-empty bytes")
        self._bytes_received += len(pcm)
        seconds = self._bytes_received / (
            self.policy.sample_rate_hz * self.policy.sample_width_bytes * self.policy.channels
        )
        if seconds > self.policy.max_utterance_seconds:
            raise StreamingSTTError("max utterance duration exceeded")
        return self.engine.push_pcm(bytes(pcm))

    def finish(self) -> list[StreamingTranscript]:
        if not self._started or self._finished:
            raise StreamingSTTError("streaming session is not active")
        events = self.engine.finish()
        self._finished = True
        return events

    def reset(self) -> None:
        self.engine.reset()
        self._started = False
        self._finished = False
        self._bytes_received = 0
