from __future__ import annotations

import time
from typing import Any

import speech_recognition as sr

from friday.stt.base import STTProviderError, STTResult


class GoogleSTTProvider:
    name = "google"

    def __init__(self, credentials_path: str = "", language_code: str = "th-TH") -> None:
        self.credentials_path = credentials_path.strip()
        self.language_code = language_code

    def _free_fallback(self, recognizer: Any, audio: Any, started: float) -> STTResult:
        try:
            text = recognizer.recognize_google(audio, language=self.language_code)
            return STTResult(
                provider=self.name,
                text=text,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                fallback_used=True,
                metadata={"backend": "recognize_google"},
            )
        except sr.UnknownValueError:
            return STTResult(
                provider=self.name,
                text=None,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                unclear=True,
                fallback_used=True,
                metadata={"backend": "recognize_google"},
            )
        except sr.RequestError as exc:
            raise STTProviderError("google_free_request_failed") from exc

    def transcribe(self, recognizer: Any, audio: Any) -> STTResult:
        started = time.perf_counter()

        # Phase 0 intentionally removed the workstation-specific credential path from source.
        # If no Cloud credentials are configured, preserve the previous degraded-but-working
        # behavior by going straight to SpeechRecognition's free Google endpoint.
        if not self.credentials_path:
            return self._free_fallback(recognizer, audio, started)

        try:
            text = recognizer.recognize_google_cloud(
                audio,
                credentials_json_path=self.credentials_path,
                language_code=self.language_code,
            )
            return STTResult(
                provider=self.name,
                text=text,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                metadata={"backend": "google_cloud"},
            )
        except sr.UnknownValueError:
            # Cloud accepted the request but could not understand this audio. Retrying the same
            # sample against the lower-accuracy endpoint is noise, not resilience.
            return STTResult(
                provider=self.name,
                text=None,
                latency_ms=round((time.perf_counter() - started) * 1000, 1),
                unclear=True,
                metadata={"backend": "google_cloud"},
            )
        except sr.RequestError:
            return self._free_fallback(recognizer, audio, started)
