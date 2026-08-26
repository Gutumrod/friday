"""Phase 1 STT provider tests. No microphone, cloud account, Typhoon model, or GPU required."""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import speech_recognition as sr

from friday.stt.base import STTResult
from friday.stt.factory import create_stt_provider
from friday.stt.google import GoogleSTTProvider
from friday.stt.runtime import install_stt_provider
from friday.stt.typhoon import TyphoonSTTProvider


class FakeRecognizer:
    def __init__(self):
        self.cloud_result = "เปิดแอร์ยี่สิบห้าองศา"
        self.free_result = "เปิดทีวี"
        self.cloud_error = None
        self.free_error = None
        self.cloud_calls = 0
        self.free_calls = 0

    def recognize_google_cloud(self, audio, credentials_json_path=None, language_code=None):
        self.cloud_calls += 1
        if self.cloud_error:
            raise self.cloud_error
        return self.cloud_result

    def recognize_google(self, audio, language=None):
        self.free_calls += 1
        if self.free_error:
            raise self.free_error
        return self.free_result


class FakeAudio:
    def get_wav_data(self, convert_rate=None, convert_width=None):
        if convert_rate != 16000 or convert_width != 2:
            raise AssertionError("Typhoon adapter must normalize AudioData to 16 kHz/16-bit WAV")
        return b"RIFFfake-wave-data"


def check_google_cloud_success():
    recognizer = FakeRecognizer()
    result = GoogleSTTProvider("C:/fake/credentials.json").transcribe(recognizer, object())
    assert result.text == "เปิดแอร์ยี่สิบห้าองศา"
    assert result.provider == "google"
    assert result.metadata["backend"] == "google_cloud"
    assert not result.fallback_used
    assert recognizer.cloud_calls == 1 and recognizer.free_calls == 0


def check_google_request_error_fallback():
    recognizer = FakeRecognizer()
    recognizer.cloud_error = sr.RequestError("quota")
    result = GoogleSTTProvider("C:/fake/credentials.json").transcribe(recognizer, object())
    assert result.text == "เปิดทีวี"
    assert result.fallback_used
    assert result.metadata["backend"] == "recognize_google"
    assert recognizer.cloud_calls == 1 and recognizer.free_calls == 1


def check_google_unclear_does_not_fallback():
    recognizer = FakeRecognizer()
    recognizer.cloud_error = sr.UnknownValueError()
    result = GoogleSTTProvider("C:/fake/credentials.json").transcribe(recognizer, object())
    assert result.text is None and result.unclear
    assert recognizer.cloud_calls == 1 and recognizer.free_calls == 0


def check_google_without_credentials_uses_free_endpoint():
    recognizer = FakeRecognizer()
    result = GoogleSTTProvider("").transcribe(recognizer, object())
    assert result.text == "เปิดทีวี"
    assert result.fallback_used
    assert recognizer.cloud_calls == 0 and recognizer.free_calls == 1


def check_typhoon_file_adapter_and_cleanup():
    seen = {}

    def fake_transcribe(path):
        seen["path"] = path
        assert os.path.exists(path)
        with open(path, "rb") as f:
            assert f.read() == b"RIFFfake-wave-data"
        return {"text": "ทดสอบไต้ฝุ่น"}

    result = TyphoonSTTProvider(transcribe_fn=fake_transcribe).transcribe(None, FakeAudio())
    assert result.text == "ทดสอบไต้ฝุ่น"
    assert result.provider == "typhoon"
    assert result.metadata["mode"] == "file_adapter"
    assert not os.path.exists(seen["path"]), "temporary WAV must be deleted after transcription"


def check_factory_defaults_to_google():
    original = os.environ.get("FRIDAY_STT_PROVIDER")
    try:
        os.environ.pop("FRIDAY_STT_PROVIDER", None)
        assert create_stt_provider().name == "google"
    finally:
        if original is not None:
            os.environ["FRIDAY_STT_PROVIDER"] = original


def check_runtime_installs_provider_and_logs_metadata():
    records = []

    class FakeProvider:
        name = "fake"

        def transcribe(self, recognizer, audio):
            return STTResult(
                provider="fake",
                text="เปิดทีวี",
                latency_ms=12.3,
                metadata={"backend": "unit"},
            )

    core = SimpleNamespace(
        _recognize_speech=lambda *_: "legacy",
        _latency=SimpleNamespace(record=lambda event, **payload: records.append((event, payload))),
    )
    install_stt_provider(core, provider=FakeProvider(), emit_warnings=False)
    assert core.FRIDAY_STT_PROVIDER_NAME == "fake"
    assert core._recognize_speech(object(), object()) == "เปิดทีวี"
    assert records and records[0][0] == "stt_provider_result"
    assert records[0][1]["provider"] == "fake"


TESTS = [
    check_google_cloud_success,
    check_google_request_error_fallback,
    check_google_unclear_does_not_fallback,
    check_google_without_credentials_uses_free_endpoint,
    check_typhoon_file_adapter_and_cleanup,
    check_factory_defaults_to_google,
    check_runtime_installs_provider_and_logs_metadata,
]


if __name__ == "__main__":
    failed = []
    for test in TESTS:
        try:
            test()
            print(f"[PASS] {test.__name__}")
        except Exception as exc:
            failed.append((test.__name__, exc))
            print(f"[FAIL] {test.__name__}: {type(exc).__name__}: {exc}")
    if failed:
        raise SystemExit(1)
    print(f"Phase 1 STT provider checks passed: {len(TESTS)}/{len(TESTS)}")
