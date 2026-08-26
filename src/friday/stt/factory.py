from __future__ import annotations

import os
import platform

from friday.stt.base import STTProviderError
from friday.stt.google import GoogleSTTProvider
from friday.stt.typhoon import TyphoonSTTProvider

SUPPORTED_STT_PROVIDERS = ("google", "typhoon")


def selected_provider_name() -> str:
    return os.environ.get("FRIDAY_STT_PROVIDER", "google").strip().lower() or "google"


def create_stt_provider(name: str | None = None):
    selected = (name or selected_provider_name()).strip().lower()
    if selected == "google":
        return GoogleSTTProvider(
            credentials_path=os.environ.get("GOOGLE_CLOUD_CREDS_PATH", ""),
            language_code=os.environ.get("FRIDAY_STT_LANGUAGE", "th-TH").strip() or "th-TH",
        )
    if selected == "typhoon":
        return TyphoonSTTProvider()
    raise STTProviderError(
        f"unsupported_stt_provider: {selected}; expected one of {', '.join(SUPPORTED_STT_PROVIDERS)}"
    )


def provider_warnings(name: str | None = None) -> list[str]:
    selected = (name or selected_provider_name()).strip().lower()
    warnings: list[str] = []
    if selected == "typhoon" and platform.system().lower() == "windows":
        warnings.append(
            "Typhoon ASR is selected on Windows; upstream does not officially support Windows yet, so live validation is required"
        )
    return warnings
