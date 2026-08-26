from __future__ import annotations

import os
import tempfile
import time
from typing import Any, Callable

from friday.stt.base import STTProviderError, STTResult, STTUnavailableError


class TyphoonSTTProvider:
    """Optional Typhoon ASR adapter for Phase 1 non-streaming parity tests.

    This adapter deliberately converts SpeechRecognition AudioData to a temporary 16 kHz WAV
    and uses the packaged file transcription API. True chunked/streaming microphone handling
    belongs to Phase 3 after the real-device benchmark gate passes.
    """

    name = "typhoon"

    def __init__(self, transcribe_fn: Callable[[str], Any] | None = None) -> None:
        self._transcribe_fn = transcribe_fn

    def _load_transcribe(self) -> Callable[[str], Any]:
        if self._transcribe_fn is not None:
            return self._transcribe_fn
        try:
            from typhoon_asr import transcribe
        except Exception as exc:
            raise STTUnavailableError(
                "typhoon_asr_unavailable: install/test the optional typhoon-asr runtime before selecting it"
            ) from exc
        self._transcribe_fn = transcribe
        return transcribe

    def transcribe(self, recognizer: Any, audio: Any) -> STTResult:
        del recognizer  # Provider contract keeps parity with Google; Typhoon does not need it.
        started = time.perf_counter()
        transcribe_fn = self._load_transcribe()
        path = ""
        try:
            wav_bytes = audio.get_wav_data(convert_rate=16000, convert_width=2)
            with tempfile.NamedTemporaryFile(prefix="friday-stt-", suffix=".wav", delete=False) as f:
                f.write(wav_bytes)
                path = f.name

            raw = transcribe_fn(path)
            if isinstance(raw, dict):
                text = str(raw.get("text") or "").strip()
            else:
                text = str(raw or "").strip()
            return STTResult(
                provider=self.name,
                text=text or None,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                unclear=not bool(text),
                metadata={"mode": "file_adapter", "sample_rate_hz": 16000},
            )
        except STTUnavailableError:
            raise
        except Exception as exc:
            raise STTProviderError("typhoon_transcription_failed") from exc
        finally:
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass
