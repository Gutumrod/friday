import contextvars
import json
import os
import platform
import time
import uuid
from contextlib import contextmanager
from datetime import datetime


_current_turn = contextvars.ContextVar("friday_latency_turn", default=None)


def _now_ms():
    return time.perf_counter() * 1000


class LatencyTurn:
    def __init__(self, log_dir, source="voice_loop"):
        self.turn_id = str(uuid.uuid4())
        self.source = source
        self.log_dir = log_dir
        self.started_at = datetime.now().isoformat(timespec="milliseconds")
        self._start_ms = _now_ms()
        self._marks = {}
        self.metrics = {}
        self.events = []
        self.metadata = {
            "platform": platform.system(),
            "python": platform.python_version(),
        }
        self._token = _current_turn.set(self)

    def mark(self, name, value=None):
        self._marks[name] = _now_ms()
        if value is not None:
            self.metadata[name] = value

    @contextmanager
    def span(self, name):
        start = _now_ms()
        try:
            yield
        finally:
            self.metrics[f"{name}_latency_ms"] = round(_now_ms() - start, 1)

    def record(self, event_type, **data):
        payload = {"type": event_type, "at_ms": round(_now_ms() - self._start_ms, 1)}
        payload.update(data)
        self.events.append(payload)

    def set_metric(self, name, value):
        self.metrics[name] = value

    def finish(self, path_type="unknown", error=None):
        finished_ms = _now_ms()
        total_ms = round(finished_ms - self._start_ms, 1)
        self.metrics["total_observed_latency_ms"] = total_ms
        self.metrics["total_turn_latency_ms"] = total_ms
        record = {
            "schema_version": 1,
            "turn_id": self.turn_id,
            "source": self.source,
            "started_at": self.started_at,
            "finished_at": datetime.now().isoformat(timespec="milliseconds"),
            "path_type": path_type,
            "metrics": self.metrics,
            "metadata": self.metadata,
            "events": self.events,
        }
        if error:
            record["error"] = str(error)
        try:
            self._write(record)
        except Exception as e:
            print(f"⚠️ Latency log write failed (non-fatal): {e}")
        finally:
            _current_turn.reset(self._token)
        return record

    def _write(self, record):
        os.makedirs(self.log_dir, exist_ok=True)
        filename = datetime.now().strftime("%Y-%m-%d") + ".jsonl"
        path = os.path.join(self.log_dir, filename)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def begin_turn(log_dir, source="voice_loop"):
    return LatencyTurn(log_dir=log_dir, source=source)


def current_turn():
    return _current_turn.get()


def mark(name, value=None):
    turn = current_turn()
    if turn:
        turn.mark(name, value=value)


@contextmanager
def span(name):
    turn = current_turn()
    if not turn:
        yield
        return
    with turn.span(name):
        yield


def record(event_type, **data):
    turn = current_turn()
    if turn:
        turn.record(event_type, **data)


def set_metric(name, value):
    turn = current_turn()
    if turn:
        turn.set_metric(name, value)


def milliseconds_since(mark_name):
    turn = current_turn()
    if not turn or mark_name not in turn._marks:
        return None
    return round(_now_ms() - turn._marks[mark_name], 1)
