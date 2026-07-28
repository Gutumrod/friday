from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import quote, urlparse

import requests
import websockets


if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TOKEN_RE = re.compile(r'window\.__HERMES_SESSION_TOKEN__="([^"]+)"|__HERMES_SESSION_TOKEN__="([^"]+)"')
PROBE_ENDPOINTS = ("/api/health", "/api/status", "/api/model/info", "/api/cron/jobs", "/openapi.json")
MANUAL_RUNTIME_ROUTES = {
    "/api/ws": {
        "methods": ["WEBSOCKET"],
        "source": "manual",
        "listed_in_openapi": False,
        "rpc_methods": ["session.create", "prompt.submit"],
    }
}


class HermesClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class HermesConfig:
    dashboard_url: str
    connect_timeout_seconds: float
    hard_timeout_seconds: float
    context_budget_tokens: int
    context_policy: str
    shadow_log_dir: str


def make_correlation_id(prefix: str = "ffh") -> str:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{now}_{uuid.uuid4().hex[:8]}"


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


def _redact_url(url: str) -> str:
    return re.sub(r"([?&](?:token|ticket)=)[^&\s;]+", r"\1<redacted>", url)


def _redact_text(text: str) -> str:
    return re.sub(r"\bBearer\s+[^,\s;]+", "Bearer <redacted>", _redact_url(text))


def _jsonl_append(log_dir: str, record: dict[str, Any]) -> str:
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, datetime.now().strftime("%Y-%m-%d") + ".jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return path


class HermesDashboardClient:
    def __init__(self, config: HermesConfig) -> None:
        self.config = config
        self.dashboard_url = config.dashboard_url.rstrip("/")

    def fetch_session_token(self) -> tuple[str, dict[str, Any]]:
        started = time.perf_counter()
        try:
            response = requests.get(self.dashboard_url + "/", timeout=self.config.connect_timeout_seconds)
        except requests.RequestException as exc:
            raise HermesClientError(f"dashboard_unreachable: {exc}") from exc
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        if response.status_code >= 400:
            raise HermesClientError(f"dashboard_http_{response.status_code}")
        match = TOKEN_RE.search(response.text)
        if not match:
            raise HermesClientError("session_token_not_found")
        token = match.group(1) or match.group(2)
        evidence = {
            "dashboard_status": response.status_code,
            "dashboard_latency_ms": latency_ms,
            "token_present": True,
            "token_length": len(token),
        }
        return token, evidence

    def probe_endpoint(self, path: str, token: str | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            response = requests.get(
                self.dashboard_url + path,
                headers=headers,
                timeout=self.config.connect_timeout_seconds,
            )
            body: Any
            try:
                body = response.json()
            except ValueError:
                body = None
            return {
                "path": path,
                "ok": response.status_code < 400,
                "status_code": response.status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                "content_length": len(response.content or b""),
                "json_keys": sorted(body.keys())[:20] if isinstance(body, dict) else [],
            }
        except requests.RequestException as exc:
            return {
                "path": path,
                "ok": False,
                "status_code": None,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                "error": str(exc),
            }

    def fetch_openapi(self, token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(
                self.dashboard_url + "/openapi.json",
                headers=headers,
                timeout=self.config.connect_timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise HermesClientError(f"openapi_fetch_failed: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("paths"), dict):
            raise HermesClientError("openapi_invalid_shape")
        return data

    def build_endpoint_manifest(self, openapi: dict[str, Any]) -> dict[str, Any]:
        paths = openapi.get("paths", {})
        manifest_paths: dict[str, Any] = {}
        for path, operations in paths.items():
            if not isinstance(operations, dict):
                continue
            manifest_paths[path] = {
                "methods": sorted(method.upper() for method in operations if method.lower() in {
                    "get", "post", "put", "patch", "delete",
                }),
                "source": "openapi",
                "listed_in_openapi": True,
            }
        manifest_paths.update(MANUAL_RUNTIME_ROUTES)
        return {
            "generated_at": _now_iso(),
            "dashboard_url": self.dashboard_url,
            "openapi_version": openapi.get("openapi"),
            "api_version": (openapi.get("info") or {}).get("version") if isinstance(openapi.get("info"), dict) else None,
            "path_count": len(paths),
            "manual_runtime_routes": sorted(MANUAL_RUNTIME_ROUTES),
            "paths": manifest_paths,
        }

    def probe_dashboard(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "generated_at": _now_iso(),
            "dashboard_url": self.dashboard_url,
            "probes": [],
            "manifest": None,
            "error": None,
        }
        try:
            token, token_evidence = self.fetch_session_token()
            record["auth"] = token_evidence
            for path in PROBE_ENDPOINTS:
                record["probes"].append(self.probe_endpoint(path, token=token))
            openapi = self.fetch_openapi(token)
            record["manifest"] = self.build_endpoint_manifest(openapi)
        except Exception as exc:
            record["error"] = str(exc)
        return record

    async def submit_prompt(self, text: str, *, correlation_id: str) -> dict[str, Any]:
        token, auth_evidence = self.fetch_session_token()
        parsed = urlparse(self.dashboard_url)
        scheme = "wss" if parsed.scheme == "https" else "ws"
        ws_url = f"{scheme}://{parsed.netloc}{parsed.path.rstrip('/')}/api/ws?token={quote(token)}"
        started = time.perf_counter()
        first_event_at: float | None = None
        next_id = 1
        session_id: str | None = None
        streaming_text = ""
        final_text = ""

        def frame(method: str, params: dict[str, Any]) -> str:
            nonlocal next_id
            payload = {"jsonrpc": "2.0", "id": next_id, "method": method, "params": params}
            next_id += 1
            return json.dumps(payload, ensure_ascii=False)

        try:
            async with websockets.connect(
                ws_url,
                open_timeout=self.config.connect_timeout_seconds,
                close_timeout=2,
                ping_interval=None,
            ) as websocket:
                deadline = time.perf_counter() + self.config.hard_timeout_seconds
                while True:
                    remaining = deadline - time.perf_counter()
                    if remaining <= 0:
                        raise TimeoutError("hermes_hard_timeout")
                    raw = await asyncio.wait_for(websocket.recv(), timeout=remaining)
                    message = json.loads(raw)
                    if first_event_at is None:
                        first_event_at = time.perf_counter()

                    if message.get("method") == "event":
                        params = message.get("params") or {}
                        event_type = params.get("type")
                        payload = params.get("payload") or {}
                        if event_type == "gateway.ready":
                            await websocket.send(frame("session.create", {"cols": 100, "source": "friday_shadow"}))
                        elif event_type == "message.delta" and isinstance(payload.get("text"), str):
                            streaming_text += payload["text"]
                        elif event_type == "message.complete":
                            if isinstance(payload.get("text"), str):
                                final_text = payload["text"]
                            elif isinstance(payload.get("message"), str):
                                final_text = payload["message"]
                            elif streaming_text.strip():
                                final_text = streaming_text
                            break
                        elif event_type == "error":
                            raise HermesClientError(str(payload.get("message") or payload))
                        continue

                    if message.get("error"):
                        raise HermesClientError(str(message["error"].get("message") or message["error"]))
                    if message.get("id") == 1 and isinstance(message.get("result"), dict):
                        session_id = message["result"].get("session_id")
                        if not session_id:
                            raise HermesClientError("session_id_missing")
                        await websocket.send(frame("prompt.submit", {"session_id": session_id, "text": text}))
                    elif message.get("id") == 2:
                        # prompt.submit normally returns quickly while completion arrives as events.
                        continue
        except Exception as exc:
            total_ms = round((time.perf_counter() - started) * 1000, 1)
            return {
                "correlation_id": correlation_id,
                "status": "error",
                "error": _redact_text(str(exc)),
                "hermes_ttfb_ms": round((first_event_at - started) * 1000, 1) if first_event_at else None,
                "hermes_total_latency_ms": total_ms,
                "ws_url": _redact_url(ws_url),
                "token_present": auth_evidence["token_present"],
            }

        return {
            "correlation_id": correlation_id,
            "status": "ok",
            "error": None,
            "hermes_ttfb_ms": round((first_event_at - started) * 1000, 1) if first_event_at else None,
            "hermes_total_latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "response_text": final_text,
            "session_id": session_id,
            "ws_url": _redact_url(ws_url),
            "token_present": auth_evidence["token_present"],
        }

    def shadow_user_text(self, text: str, *, correlation_id: str) -> dict[str, Any]:
        started_record = {
            "created_at": _now_iso(),
            "correlation_id": correlation_id,
            "user_text": text,
            "mode": "shadow",
            "context_policy": self.config.context_policy,
            "context_budget_tokens": self.config.context_budget_tokens,
            "status": "started",
            "hermes_ttfb_ms": None,
            "hermes_total_latency_ms": None,
            "error": None,
        }
        try:
            result = asyncio.run(self.submit_prompt(text, correlation_id=correlation_id))
            record = {**started_record, **result, "response_text_length": len(result.get("response_text") or "")}
            record.pop("response_text", None)
        except Exception as exc:
            record = {**started_record, "status": "error", "error": _redact_text(str(exc))}
        _jsonl_append(self.config.shadow_log_dir, record)
        return record


def schedule_shadow_request(client: HermesDashboardClient, text: str, *, correlation_id: str) -> threading.Thread:
    thread = threading.Thread(
        target=client.shadow_user_text,
        kwargs={"text": text, "correlation_id": correlation_id},
        daemon=True,
        name=f"FridayHermesShadow-{correlation_id[-8:]}",
    )
    thread.start()
    return thread


def _default_config() -> HermesConfig:
    from friday.config import (
        FRIDAY_HERMES_CONTEXT_BUDGET_TOKENS,
        FRIDAY_HERMES_CONTEXT_POLICY,
        HERMES_CONNECT_TIMEOUT_SECONDS,
        HERMES_DASHBOARD_URL,
        HERMES_SHADOW_LOG_DIR,
        HERMES_SYNC_HARD_TIMEOUT_SECONDS,
    )

    return HermesConfig(
        dashboard_url=HERMES_DASHBOARD_URL,
        connect_timeout_seconds=HERMES_CONNECT_TIMEOUT_SECONDS,
        hard_timeout_seconds=HERMES_SYNC_HARD_TIMEOUT_SECONDS,
        context_budget_tokens=FRIDAY_HERMES_CONTEXT_BUDGET_TOKENS,
        context_policy=FRIDAY_HERMES_CONTEXT_POLICY,
        shadow_log_dir=HERMES_SHADOW_LOG_DIR,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Friday for Hermes Phase 0 probe/smoke client")
    parser.add_argument("--probe", action="store_true", help="probe dashboard REST endpoints and print manifest summary")
    parser.add_argument("--smoke", metavar="TEXT", help="submit one WebSocket prompt to Hermes")
    parser.add_argument("--write-audit", metavar="PATH", help="write probe JSON to a file")
    args = parser.parse_args()

    client = HermesDashboardClient(_default_config())
    if args.probe:
        record = client.probe_dashboard()
        if args.write_audit:
            os.makedirs(os.path.dirname(os.path.abspath(args.write_audit)), exist_ok=True)
            with open(args.write_audit, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
        summary = {
            "dashboard_url": record["dashboard_url"],
            "error": record["error"],
            "probes": record["probes"],
            "path_count": (record.get("manifest") or {}).get("path_count"),
            "manual_runtime_routes": (record.get("manifest") or {}).get("manual_runtime_routes"),
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.smoke:
        correlation_id = make_correlation_id()
        result = asyncio.run(client.submit_prompt(args.smoke, correlation_id=correlation_id))
        printable = {k: v for k, v in result.items() if k != "response_text"}
        printable["response_text_preview"] = (result.get("response_text") or "")[:500]
        print(json.dumps(printable, ensure_ascii=False, indent=2))
        return 0 if result.get("status") == "ok" else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
