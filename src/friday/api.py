"""FastAPI service entrypoint for Friday UI.

This module intentionally does not start the walkie-talkie voice loop. It exposes a thin
service boundary over friday.core so the UI can inspect state, send text commands, and
confirm gated tool calls without weakening the existing confirm gate.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from collections import deque
from datetime import datetime
from typing import Any, Deque

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from friday import core
from friday.config import HISTORY_DIR, MODEL_NAME, OLLAMA_URL


EVENT_TYPES = {
    "listening_started",
    "stt_result",
    "thinking_started",
    "llm_response",
    "tool_requested",
    "confirm_required",
    "tool_executed",
    "tts_started",
    "tts_finished",
    "hermes_notified",
    "error",
}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ToolConfirmRequest(BaseModel):
    confirmation_id: str
    confirm: bool = True


class VoiceStateResponse(BaseModel):
    running: bool
    message: str


class Event(BaseModel):
    id: str
    type: str
    created_at: str
    payload: dict[str, Any] = Field(default_factory=dict)


class _ApiState:
    def __init__(self) -> None:
        self.history: list[dict[str, str]] = [{"role": "system", "content": core.build_system_prompt()}]
        self.pending_confirm: dict[str, dict[str, str]] = {}
        self.voice_running = False
        self.events: Deque[Event] = deque(maxlen=200)
        self.websockets: set[WebSocket] = set()
        self.lock = asyncio.Lock()


state = _ApiState()
app = FastAPI(title="Friday API Service", version="0.1.0")


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


async def _emit(event_type: str, payload: dict[str, Any] | None = None) -> Event:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unknown event type: {event_type}")
    event = Event(id=uuid.uuid4().hex, type=event_type, created_at=_now_iso(), payload=payload or {})
    state.events.append(event)
    dead: list[WebSocket] = []
    for websocket in list(state.websockets):
        try:
            await websocket.send_json(event.model_dump())
        except Exception:
            dead.append(websocket)
    for websocket in dead:
        state.websockets.discard(websocket)
    return event


def _tool_summaries() -> list[dict[str, Any]]:
    tools = []
    for schema in core.TOOL_SCHEMAS:
        fn = schema["function"]
        name = fn["name"]
        tools.append(
            {
                "name": name,
                "description": fn.get("description", ""),
                "parameters": fn.get("parameters", {}),
                "confirm_required": name in core.CONFIRM_GATED,
            }
        )
    return tools


def _latest_history_file() -> str | None:
    if not os.path.isdir(HISTORY_DIR):
        return None
    candidates = [
        os.path.join(HISTORY_DIR, name)
        for name in os.listdir(HISTORY_DIR)
        if core.SESSION_FILE_PATTERN.match(name) or core.LEGACY_DAY_FILE_PATTERN.match(name)
    ]
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def _recent_events(limit: int = 50) -> list[dict[str, Any]]:
    return [event.model_dump() for event in list(state.events)[-limit:]]


def _status_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "friday-api",
        "model": MODEL_NAME,
        "ollama_url": OLLAMA_URL,
        "voice_running": state.voice_running,
        "pending_confirmations": len(state.pending_confirm),
        "tool_count": len(core.TOOLS),
        "event_types": sorted(EVENT_TYPES),
    }


@app.get("/api/status")
async def api_status() -> dict[str, Any]:
    return _status_payload()


@app.get("/api/tools")
async def api_tools() -> dict[str, Any]:
    return {"tools": _tool_summaries()}


@app.get("/api/memory/facts")
async def api_memory_facts() -> dict[str, Any]:
    return {"facts": core.load_facts()}


@app.get("/api/history/latest")
async def api_history_latest() -> dict[str, Any]:
    path = _latest_history_file()
    if path is None:
        return {"path": None, "content": ""}
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"path": path, "content": content}


@app.post("/api/chat")
async def api_chat(request: ChatRequest) -> dict[str, Any]:
    user_input = request.message.strip()
    async with state.lock:
        await _emit("stt_result", {"text": user_input, "source": "text"})
        state.history.append({"role": "user", "content": user_input})
        await _emit("thinking_started", {"message": user_input})

        try:
            message = await asyncio.to_thread(core.ask_ollama, user_input, state.history[:-1], core.TOOL_SCHEMAS)
        except Exception as exc:
            await _emit("error", {"stage": "llm", "error": str(exc)})
            raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

        content = (message.get("content") or "").strip()
        tool_calls = message.get("tool_calls") or []
        if content:
            await _emit("llm_response", {"content": content})

        if tool_calls:
            await _emit("tool_requested", {"tool_calls": tool_calls})

        gated = core.find_first_gated_tool_call(tool_calls)
        if gated:
            name, args = gated
            confirmation_id = uuid.uuid4().hex
            question = core.CONFIRM_GATED[name]["question"](args)
            state.pending_confirm[confirmation_id] = {"tool_name": name, "args": args}
            reply = (content + " " if content else "") + question
            state.history.append({"role": "assistant", "content": reply})
            await _emit(
                "confirm_required",
                {
                    "confirmation_id": confirmation_id,
                    "tool_name": name,
                    "args": args,
                    "question": question,
                },
            )
            return {
                "reply": reply,
                "tool_calls": tool_calls,
                "pending_confirmation": {
                    "confirmation_id": confirmation_id,
                    "tool_name": name,
                    "args": args,
                    "question": question,
                },
            }

        if tool_calls:
            try:
                tool_output = await asyncio.to_thread(core.run_native_tools, tool_calls)
            except Exception as exc:
                await _emit("error", {"stage": "tool", "error": str(exc)})
                raise HTTPException(status_code=500, detail=f"Tool execution failed: {exc}") from exc
            reply = (content + " " + tool_output).strip()
            await _emit("tool_executed", {"output": tool_output})
            if any(tc["function"]["name"] == "notify_hermes" for tc in tool_calls):
                await _emit("hermes_notified", {"output": tool_output})
        else:
            reply = content

        state.history.append({"role": "assistant", "content": reply})
        if len(state.history) > 21:
            state.history = [state.history[0]] + state.history[-20:]
        return {"reply": reply, "tool_calls": tool_calls, "pending_confirmation": None}


@app.post("/api/tool/confirm")
async def api_tool_confirm(request: ToolConfirmRequest) -> dict[str, Any]:
    async with state.lock:
        pending = state.pending_confirm.pop(request.confirmation_id, None)
        if pending is None:
            raise HTTPException(status_code=404, detail="confirmation_id not found")

        tool_name = pending["tool_name"]
        args = pending["args"]
        gate = core.CONFIRM_GATED[tool_name]
        if not request.confirm:
            reply = gate["cancel"](args)
            state.history.append({"role": "assistant", "content": reply})
            await _emit("tool_executed", {"tool_name": tool_name, "args": args, "cancelled": True, "output": reply})
            return {"reply": reply, "executed": False}

        try:
            output = await asyncio.to_thread(gate["execute"], args)
        except Exception as exc:
            await _emit("error", {"stage": "tool_confirm", "tool_name": tool_name, "error": str(exc)})
            raise HTTPException(status_code=500, detail=f"Tool execution failed: {exc}") from exc

        state.history.append({"role": "assistant", "content": output})
        await _emit("tool_executed", {"tool_name": tool_name, "args": args, "cancelled": False, "output": output})
        if tool_name == "notify_hermes":
            await _emit("hermes_notified", {"output": output})
        return {"reply": output, "executed": True}


@app.post("/api/voice/start", response_model=VoiceStateResponse)
async def api_voice_start() -> VoiceStateResponse:
    state.voice_running = True
    await _emit("listening_started", {"source": "api"})
    return VoiceStateResponse(running=True, message="voice state marked as started; realtime audio loop is out of scope for this phase")


@app.post("/api/voice/stop", response_model=VoiceStateResponse)
async def api_voice_stop() -> VoiceStateResponse:
    state.voice_running = False
    return VoiceStateResponse(running=False, message="voice state marked as stopped")


@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket) -> None:
    await websocket.accept()
    state.websockets.add(websocket)
    try:
        await websocket.send_json({"type": "snapshot", "events": _recent_events()})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.websockets.discard(websocket)


__all__ = ["app"]
