"""Pure Phase 2 benchmark metric checks; no audio device/provider runtime required."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from benchmark_stt import char_error_rate, command_pass, edit_distance, normalize_text, percentile, summarize


def check_normalize_text():
    assert normalize_text(" Friday, เปิด YouTube! ") == "fridayเปิดyoutube"


def check_edit_distance():
    assert edit_distance("abc", "abc") == 0
    assert edit_distance("abc", "axc") == 1
    assert edit_distance("", "abc") == 3


def check_cer():
    assert char_error_rate("เปิดทีวี", "เปิดทีวี") == 0
    assert char_error_rate("abc", "axc") == 1 / 3


def check_command_pass():
    assert command_pass("ช่วยเปิดทีวีให้หน่อย", ["เปิด", "ทีวี"]) is True
    assert command_pass("ช่วยปิดทีวีให้หน่อย", ["เปิด", "ทีวี"]) is False
    assert command_pass("อะไรก็ได้", None) is None


def check_percentile():
    assert percentile([10, 20, 30, 40], 0.95) == 40
    assert percentile([], 0.95) is None


def check_summary():
    rows = [
        {"provider": "google", "status": "ok", "latency_ms": 100.0, "exact_match": True, "cer": 0.0, "command_pass": True},
        {"provider": "google", "status": "ok", "latency_ms": 200.0, "exact_match": False, "cer": 0.2, "command_pass": False},
        {"provider": "typhoon", "status": "error", "latency_ms": 0.0, "exact_match": False, "cer": 1.0, "command_pass": False},
    ]
    result = summarize(rows)
    google = result["providers"]["google"]
    assert google["total"] == 2 and google["completed"] == 2
    assert google["exact_accuracy"] == 0.5
    assert google["mean_cer"] == 0.1
    assert google["command_accuracy"] == 0.5
    assert google["latency_median_ms"] == 150.0
    typhoon = result["providers"]["typhoon"]
    assert typhoon["errors"] == 1 and typhoon["completed"] == 0


TESTS = [
    check_normalize_text,
    check_edit_distance,
    check_cer,
    check_command_pass,
    check_percentile,
    check_summary,
]


if __name__ == "__main__":
    failures = []
    for test in TESTS:
        try:
            test()
            print(f"[PASS] {test.__name__}")
        except Exception as exc:
            failures.append((test.__name__, exc))
            print(f"[FAIL] {test.__name__}: {type(exc).__name__}: {exc}")
    if failures:
        raise SystemExit(1)
    print(f"Phase 2 benchmark metric checks passed: {len(TESTS)}/{len(TESTS)}")
