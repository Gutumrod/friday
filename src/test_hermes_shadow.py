"""Targeted non-live safety checks for Friday Hermes Phase 0 shadow mode."""

import json
import os
import shutil
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import friday_walkie_talkie as fw
from friday import hermes_client


results = []


def check(name, fn):
    try:
        out = fn()
        results.append((name, True, out))
    except Exception as exc:
        results.append((name, False, f"{type(exc).__name__}: {exc}"))


def check_hermes_shadow_default_off():
    orig_mode = fw.FRIDAY_FOR_HERMES_MODE
    orig_schedule = fw._hermes_client.schedule_shadow_request
    calls = []
    fw.FRIDAY_FOR_HERMES_MODE = "off"
    fw._hermes_client.schedule_shadow_request = lambda *args, **kwargs: calls.append((args, kwargs))
    try:
        result = fw.maybe_shadow_hermes_user_text("ทดสอบ")
    finally:
        fw.FRIDAY_FOR_HERMES_MODE = orig_mode
        fw._hermes_client.schedule_shadow_request = orig_schedule
    if result is not None or calls:
        raise AssertionError("shadow scheduler must stay idle when FRIDAY_FOR_HERMES_MODE=off")
    return "off mode does not schedule Hermes"


def check_hermes_shadow_requires_exact_shadow_mode():
    orig_mode = fw.FRIDAY_FOR_HERMES_MODE
    orig_schedule = fw._hermes_client.schedule_shadow_request
    calls = []
    fw._hermes_client.schedule_shadow_request = lambda *args, **kwargs: calls.append((args, kwargs))
    try:
        for mode in ("", "off", "sync", "async_only", "shadow "):
            fw.FRIDAY_FOR_HERMES_MODE = mode
            result = fw.maybe_shadow_hermes_user_text("ทดสอบ")
            if result is not None:
                raise AssertionError(f"mode {mode!r} unexpectedly returned correlation id {result!r}")
    finally:
        fw.FRIDAY_FOR_HERMES_MODE = orig_mode
        fw._hermes_client.schedule_shadow_request = orig_schedule
    if calls:
        raise AssertionError(f"non-shadow modes scheduled Hermes: {calls}")
    return "only exact shadow mode can schedule Hermes"


def check_hermes_shadow_schedule_is_fire_and_forget():
    orig_mode = fw.FRIDAY_FOR_HERMES_MODE
    orig_schedule = fw._hermes_client.schedule_shadow_request
    seen = {}

    def fake_schedule(client, text, *, correlation_id):
        seen["client"] = client
        seen["text"] = text
        seen["correlation_id"] = correlation_id
        return object()

    fw.FRIDAY_FOR_HERMES_MODE = "shadow"
    fw._hermes_client.schedule_shadow_request = fake_schedule
    try:
        correlation_id = fw.maybe_shadow_hermes_user_text("สวัสดี Hermes")
    finally:
        fw.FRIDAY_FOR_HERMES_MODE = orig_mode
        fw._hermes_client.schedule_shadow_request = orig_schedule
    if not correlation_id or not correlation_id.startswith(fw.FRIDAY_CORRELATION_ID_PREFIX + "_"):
        raise AssertionError(f"unexpected correlation id: {correlation_id}")
    if seen.get("text") != "สวัสดี Hermes" or seen.get("correlation_id") != correlation_id:
        raise AssertionError(f"shadow request was not scheduled correctly: {seen}")
    return f"scheduled with {correlation_id}"


def check_schedule_shadow_request_thread_contract():
    done = threading.Event()
    seen = {}

    class FakeClient:
        def shadow_user_text(self, *, text, correlation_id):
            seen["text"] = text
            seen["correlation_id"] = correlation_id
            done.set()

    thread = hermes_client.schedule_shadow_request(FakeClient(), "งานเงา", correlation_id="ffh_test_thread")
    if not thread.daemon:
        raise AssertionError("shadow request thread must be daemon/fire-and-forget")
    if not thread.name.startswith("FridayHermesShadow-"):
        raise AssertionError(f"unexpected shadow thread name: {thread.name}")
    if not done.wait(2):
        raise AssertionError("shadow request thread did not call client.shadow_user_text")
    if seen != {"text": "งานเงา", "correlation_id": "ffh_test_thread"}:
        raise AssertionError(f"unexpected shadow thread payload: {seen}")
    return thread.name


def _test_config(log_dir):
    return hermes_client.HermesConfig(
        dashboard_url="http://127.0.0.1:9119",
        connect_timeout_seconds=0.01,
        hard_timeout_seconds=0.01,
        context_budget_tokens=2000,
        context_policy="minimal",
        shadow_log_dir=log_dir,
    )


def check_hermes_shadow_log_redacts_response_body():
    tmp = tempfile.mkdtemp(prefix="friday-hermes-shadow-")

    class FakeClient(hermes_client.HermesDashboardClient):
        async def submit_prompt(self, text, *, correlation_id):
            return {
                "correlation_id": correlation_id,
                "status": "ok",
                "error": None,
                "hermes_ttfb_ms": 1.0,
                "hermes_total_latency_ms": 2.0,
                "response_text": "secret response body",
                "token_present": True,
                "ws_url": "ws://127.0.0.1:9119/api/ws?token=<redacted>",
            }

    try:
        record = FakeClient(_test_config(tmp)).shadow_user_text("คำสั่งทดสอบ", correlation_id="ffh_test")
        files = os.listdir(tmp)
        if len(files) != 1:
            raise AssertionError(f"expected one shadow log file, got: {files}")
        with open(os.path.join(tmp, files[0]), "r", encoding="utf-8") as handle:
            loaded = json.loads(handle.readline())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    serialized = json.dumps(loaded, ensure_ascii=False)
    if "response_text" in record or "response_text" in loaded:
        raise AssertionError("shadow log must not persist the full Hermes response body")
    if "secret response body" in serialized:
        raise AssertionError("shadow log leaked full response body")
    if "token=<redacted>" not in loaded.get("ws_url", ""):
        raise AssertionError(f"expected redacted websocket URL, got: {loaded.get('ws_url')}")
    if loaded["response_text_length"] != len("secret response body"):
        raise AssertionError(f"expected response length only, got: {loaded}")
    return "shadow log stores metadata/latency without response body"


def check_hermes_shadow_exception_log_redacts_error():
    tmp = tempfile.mkdtemp(prefix="friday-hermes-shadow-error-")

    class FakeClient(hermes_client.HermesDashboardClient):
        async def submit_prompt(self, text, *, correlation_id):
            raise RuntimeError("ws://x/api/ws?token=abc123 failed; Authorization: Bearer abc123")

    try:
        record = FakeClient(_test_config(tmp)).shadow_user_text("คำสั่งทดสอบ", correlation_id="ffh_error")
        files = os.listdir(tmp)
        if len(files) != 1:
            raise AssertionError(f"expected one shadow log file, got: {files}")
        with open(os.path.join(tmp, files[0]), "r", encoding="utf-8") as handle:
            loaded = json.loads(handle.readline())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    serialized = json.dumps(loaded, ensure_ascii=False)
    if "abc123" in serialized or "abc123" in json.dumps(record, ensure_ascii=False):
        raise AssertionError(f"secret-like token survived shadow error log: {loaded}")
    if loaded["status"] != "error":
        raise AssertionError(f"expected error status, got: {loaded}")
    return loaded["error"]


def check_hermes_error_redaction():
    redacted = hermes_client._redact_text("ws://x/api/ws?token=abc123 failed; Authorization: Bearer abc123")
    if "abc123" in redacted:
        raise AssertionError(f"secret-like token survived redaction: {redacted}")
    if "<redacted>" not in redacted:
        raise AssertionError(f"expected redaction marker, got: {redacted}")
    return redacted


check("hermes_shadow(default_off)", check_hermes_shadow_default_off)
check("hermes_shadow(exact_mode_only)", check_hermes_shadow_requires_exact_shadow_mode)
check("hermes_shadow(schedule)", check_hermes_shadow_schedule_is_fire_and_forget)
check("hermes_shadow(thread_contract)", check_schedule_shadow_request_thread_contract)
check("hermes_shadow(log_redaction)", check_hermes_shadow_log_redacts_response_body)
check("hermes_shadow(exception_redaction)", check_hermes_shadow_exception_log_redacts_error)
check("hermes_shadow(error_redaction)", check_hermes_error_redaction)

print("\n=== Friday Hermes Shadow Targeted Check ===")
for name, ok, out in results:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {out}")

failed = [result for result in results if not result[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
