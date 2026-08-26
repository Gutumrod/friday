from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import requests


class HomeAssistantError(RuntimeError):
    pass


class HomeAssistantConfigError(HomeAssistantError):
    pass


class HomeAssistantAuthError(HomeAssistantError):
    pass


@dataclass(frozen=True)
class HomeAssistantConfig:
    base_url: str
    token: str = field(repr=False)
    timeout_seconds: float = 5.0

    @classmethod
    def from_env(cls) -> "HomeAssistantConfig":
        base_url = os.environ.get("HOME_ASSISTANT_URL", "").strip().rstrip("/")
        token = os.environ.get("HOME_ASSISTANT_TOKEN", "").strip()
        raw_timeout = os.environ.get("HOME_ASSISTANT_CONNECT_TIMEOUT", "5").strip() or "5"
        if not base_url:
            raise HomeAssistantConfigError("HOME_ASSISTANT_URL is not configured")
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise HomeAssistantConfigError("HOME_ASSISTANT_URL must be an http/https URL")
        if not token:
            raise HomeAssistantConfigError("HOME_ASSISTANT_TOKEN is not configured")
        try:
            timeout = float(raw_timeout)
        except ValueError as exc:
            raise HomeAssistantConfigError("HOME_ASSISTANT_CONNECT_TIMEOUT must be a number") from exc
        if timeout <= 0:
            raise HomeAssistantConfigError("HOME_ASSISTANT_CONNECT_TIMEOUT must be greater than zero")
        return cls(base_url=base_url, token=token, timeout_seconds=timeout)


_SERVICE_PART_RE = re.compile(r"^[a-z0-9_]+$")


class HomeAssistantClient:
    def __init__(self, config: HomeAssistantConfig, *, session: Any | None = None) -> None:
        self.config = config
        self._session = session or requests.Session()

    def __repr__(self) -> str:
        return f"HomeAssistantClient(base_url={self.config.base_url!r}, timeout_seconds={self.config.timeout_seconds!r})"

    def _request(self, method: str, path: str, *, json_body: dict[str, Any] | None = None) -> Any:
        url = self.config.base_url + path
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }
        kwargs: dict[str, Any] = {
            "headers": headers,
            "timeout": self.config.timeout_seconds,
        }
        if json_body is not None:
            kwargs["json"] = json_body
        try:
            response = self._session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            raise HomeAssistantError("home_assistant_unreachable") from exc
        except Exception as exc:
            raise HomeAssistantError("home_assistant_request_failed") from exc

        if response.status_code == 401:
            raise HomeAssistantAuthError("home_assistant_unauthorized")
        if response.status_code == 404:
            raise HomeAssistantError("home_assistant_not_found")
        if response.status_code >= 400:
            raise HomeAssistantError(f"home_assistant_http_{response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise HomeAssistantError("home_assistant_invalid_json") from exc

    def health(self) -> dict[str, Any]:
        payload = self._request("GET", "/api/")
        return {
            "ok": True,
            "message": payload.get("message") if isinstance(payload, dict) else None,
        }

    def get_entity_state(self, entity_id: str) -> dict[str, Any]:
        entity_id = entity_id.strip()
        if not entity_id or "." not in entity_id:
            raise HomeAssistantError("invalid_entity_id")
        payload = self._request("GET", f"/api/states/{entity_id}")
        if not isinstance(payload, dict):
            raise HomeAssistantError("home_assistant_invalid_state_shape")
        return payload

    def list_entities(self, *, domain: str = "", limit: int = 50) -> list[dict[str, Any]]:
        if limit < 1 or limit > 200:
            raise HomeAssistantError("entity_limit_out_of_range")
        domain = domain.strip().lower()
        payload = self._request("GET", "/api/states")
        if not isinstance(payload, list):
            raise HomeAssistantError("home_assistant_invalid_states_shape")
        rows = []
        prefix = domain + "." if domain else ""
        for item in payload:
            if not isinstance(item, dict):
                continue
            entity_id = str(item.get("entity_id") or "")
            if prefix and not entity_id.startswith(prefix):
                continue
            rows.append(item)
            if len(rows) >= limit:
                break
        return rows

    def call_service(self, domain: str, service: str, service_data: dict[str, Any]) -> Any:
        domain = domain.strip().lower()
        service = service.strip().lower()
        if not _SERVICE_PART_RE.fullmatch(domain) or not _SERVICE_PART_RE.fullmatch(service):
            raise HomeAssistantError("invalid_service_name")
        if not isinstance(service_data, dict):
            raise HomeAssistantError("invalid_service_data")
        return self._request(
            "POST",
            f"/api/services/{domain}/{service}",
            json_body=service_data,
        )
