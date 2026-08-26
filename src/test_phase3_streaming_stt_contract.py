"""Phase 3 streaming contract tests. No microphone/model runtime required."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from friday.stt.streaming import (
    StreamingAudioPolicy,
    StreamingSTTError,
    StreamingSTTSession,
    StreamingTranscript,
)


class FakeEngine:
    name = "fake-stream"

    def __init__(self):
        self.calls = []
        self.sequence = 0

    def reset(self):
        self.calls.append(("reset",))
        self.sequence = 0

    def start(self, *, sample_rate_hz, sample_width_bytes, channels):
        self.calls.append(("start", sample_rate_hz, sample_width_bytes, channels))

    def push_pcm(self, pcm):
        self.sequence += 1
        self.calls.append(("push", len(pcm)))
        return [StreamingTranscript(self.sequence, f"partial-{self.sequence}", False, 10.0)]

    def finish(self):
        self.sequence += 1
        self.calls.append(("finish",))
        return [StreamingTranscript(self.sequence, "final text", True, 20.0)]


def check_policy_chunk_size():
    policy = StreamingAudioPolicy(sample_rate_hz=16000, sample_width_bytes=2, channels=1, chunk_ms=160)
    policy.validate()
    assert policy.bytes_per_chunk == 5120


def check_start_push_finish():
    engine = FakeEngine()
    session = StreamingSTTSession(engine)
    session.start()
    partial = session.push_pcm(b"\x00" * 3200)
    final = session.finish()
    assert partial[0].final is False
    assert final[0].final is True and final[0].text == "final text"
    assert engine.calls[0] == ("reset",)
    assert engine.calls[1] == ("start", 16000, 2, 1)


def check_push_before_start_rejected():
    session = StreamingSTTSession(FakeEngine())
    try:
        session.push_pcm(b"123")
    except StreamingSTTError:
        return
    raise AssertionError("push before start must fail")


def check_empty_chunk_rejected():
    session = StreamingSTTSession(FakeEngine())
    session.start()
    try:
        session.push_pcm(b"")
    except StreamingSTTError:
        return
    raise AssertionError("empty audio chunk must fail")


def check_max_duration_guard():
    policy = StreamingAudioPolicy(sample_rate_hz=100, sample_width_bytes=2, channels=1, chunk_ms=100, max_utterance_seconds=1)
    session = StreamingSTTSession(FakeEngine(), policy)
    session.start()
    session.push_pcm(b"\x00" * 200)
    try:
        session.push_pcm(b"\x00" * 2)
    except StreamingSTTError as exc:
        assert "max utterance" in str(exc)
        return
    raise AssertionError("duration overrun must fail")


def check_finish_twice_rejected():
    session = StreamingSTTSession(FakeEngine())
    session.start()
    session.finish()
    try:
        session.finish()
    except StreamingSTTError:
        return
    raise AssertionError("double finish must fail")


TESTS = [
    check_policy_chunk_size,
    check_start_push_finish,
    check_push_before_start_rejected,
    check_empty_chunk_rejected,
    check_max_duration_guard,
    check_finish_twice_rejected,
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
    print(f"Phase 3 streaming contract checks passed: {len(TESTS)}/{len(TESTS)}")
