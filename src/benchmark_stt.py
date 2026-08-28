"""Benchmark Friday STT providers against the same labeled WAV files.

Example:
  python src/benchmark_stt.py --manifest benchmarks/stt/manifest.jsonl --providers google,typhoon

Audio and result files are intentionally not committed. See benchmarks/stt/README.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import speech_recognition as sr

from friday.stt.factory import create_stt_provider


_NORMALIZE_RE = re.compile(r"[^\w\u0E00-\u0E7F]+", re.UNICODE)


def normalize_text(text: str | None) -> str:
    return _NORMALIZE_RE.sub("", (text or "").strip().lower())


def edit_distance(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (char_a != char_b),
                )
            )
        previous = current
    return previous[-1]


def char_error_rate(expected: str, actual: str | None) -> float:
    target = normalize_text(expected)
    got = normalize_text(actual)
    if not target:
        return 0.0 if not got else 1.0
    return edit_distance(target, got) / len(target)


def command_pass(actual: str | None, required_terms: list[str] | None) -> bool | None:
    if not required_terms:
        return None
    normalized_actual = normalize_text(actual)
    return all(normalize_text(term) in normalized_actual for term in required_terms)


def load_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            row = json.loads(line)
            for required in ("id", "audio", "expected", "category"):
                if not row.get(required):
                    raise ValueError(f"manifest line {line_no}: missing {required}")
            rows.append(row)
    if not rows:
        raise ValueError("manifest contains no benchmark rows")
    return rows


def read_audio(path: Path) -> sr.AudioData:
    with sr.AudioFile(str(path)) as source:
        return sr.Recognizer().record(source)


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * p)))
    return round(ordered[index], 1)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_provider: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_provider[row["provider"]].append(row)

    summary: dict[str, Any] = {"providers": {}}
    for provider, rows in sorted(by_provider.items()):
        completed = [r for r in rows if r["status"] == "ok"]
        latencies = [float(r["latency_ms"]) for r in completed]
        exact = [bool(r["exact_match"]) for r in completed]
        command_rows = [r for r in completed if r["command_pass"] is not None]
        summary["providers"][provider] = {
            "total": len(rows),
            "completed": len(completed),
            "errors": len(rows) - len(completed),
            "exact_accuracy": round(sum(exact) / len(exact), 4) if exact else None,
            "mean_cer": round(statistics.mean(r["cer"] for r in completed), 4) if completed else None,
            "command_accuracy": (
                round(sum(bool(r["command_pass"]) for r in command_rows) / len(command_rows), 4)
                if command_rows
                else None
            ),
            "latency_median_ms": round(statistics.median(latencies), 1) if latencies else None,
            "latency_p95_ms": percentile(latencies, 0.95),
        }
    return summary


def run(manifest_path: Path, providers: list[str], output_dir: Path) -> tuple[Path, Path]:
    manifest = load_manifest(manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    records_path = output_dir / f"stt_benchmark_{stamp}.jsonl"
    summary_path = output_dir / f"stt_benchmark_{stamp}_summary.json"
    records: list[dict[str, Any]] = []

    provider_objects: dict[str, Any] = {}
    for provider_name in providers:
        provider_objects[provider_name] = create_stt_provider(provider_name)

    for case in manifest:
        audio_path = Path(case["audio"])
        if not audio_path.is_absolute():
            audio_path = (manifest_path.parent / audio_path).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"benchmark audio missing: {audio_path}")
        audio = read_audio(audio_path)

        for provider_name, provider in provider_objects.items():
            base = {
                "id": case["id"],
                "category": case["category"],
                "provider": provider_name,
                "audio": str(audio_path),
                "expected": case["expected"],
                "required_terms": case.get("required_terms") or [],
            }
            try:
                result = provider.transcribe(None if provider_name == "typhoon" else sr.Recognizer(), audio)
                actual = result.text
                row = {
                    **base,
                    "status": "ok",
                    "actual": actual,
                    "exact_match": normalize_text(actual) == normalize_text(case["expected"]),
                    "cer": round(char_error_rate(case["expected"], actual), 4),
                    "command_pass": command_pass(actual, case.get("required_terms")),
                    "latency_ms": result.latency_ms,
                    "unclear": result.unclear,
                    "fallback_used": result.fallback_used,
                    "metadata": result.metadata,
                }
            except Exception as exc:
                row = {
                    **base,
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "actual": None,
                    "exact_match": False,
                    "cer": 1.0,
                    "command_pass": False if case.get("required_terms") else None,
                    "latency_ms": 0.0,
                    "unclear": False,
                    "fallback_used": False,
                    "metadata": {},
                }
            records.append(row)
            with records_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(records)
    summary.update(
        {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "manifest": str(manifest_path.resolve()),
            "record_count": len(records),
        }
    )
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return records_path, summary_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Friday Google/Typhoon STT benchmark")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--providers", default="google,typhoon")
    parser.add_argument("--output-dir", type=Path, default=Path("benchmarks/stt/results"))
    args = parser.parse_args()
    providers = [p.strip().lower() for p in args.providers.split(",") if p.strip()]
    records, summary = run(args.manifest, providers, args.output_dir)
    print(f"records: {records}")
    print(f"summary: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
