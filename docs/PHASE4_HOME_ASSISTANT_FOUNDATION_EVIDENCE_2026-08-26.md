# Phase 4 — Home Assistant Read-Only Foundation Evidence

Date: 2026-08-26
Branch: `feat/phase4-home-assistant-foundation`
Parent: `feat/phase1-stt-provider-abstraction`
Status: **CODE COMPLETE — LIVE HA GATE PENDING**

## Architecture

Friday uses Home Assistant as a smart-home control plane. This phase is read-only only.

Official Home Assistant REST contract checked 2026-08-26:

- API base is `/api/` on the Home Assistant frontend port (commonly 8123).
- requests use `Authorization: Bearer TOKEN`.
- `GET /api/states` lists entity states.
- `GET /api/states/<entity_id>` reads one entity state.
- actual device control is performed through service calls, not by writing `/api/states`; write/service calls are intentionally deferred to Phase 6.

## Implemented

- `HomeAssistantConfig.from_env()` with URL/token/timeout validation.
- token excluded from dataclass/client repr.
- safe normalized errors without response-body logging.
- read-only client methods:
  - `health()`
  - `get_entity_state()`
  - `list_entities()` with domain filter and hard limit
- optional runtime wiring:
  - `ha_status`
  - `ha_get_entity_state`
  - `ha_list_entities`
- tools register only when HA config is available.
- read-only tools remain outside `CONFIRM_GATED`.
- voice and FastAPI guarded launchers can expose the same read-only tool layer.
- `src/test_phase4_home_assistant.py` contains fake-server regression coverage without a real HA instance.

## Secrets

Real `HOME_ASSISTANT_TOKEN` must exist only in ignored local `.env`. `.env.example` contains placeholder values only.

## Required Live Gate

When Home Assistant is installed/running:

1. Create a dedicated Long-Lived Access Token.
2. Add URL/token to local `.env`.
3. Run Phase 0 + Phase 1 + Phase 4 tests.
4. Start Friday API and confirm `/api/tools` exposes the 3 HA read-only tools.
5. Run `ha_status` against the real instance.
6. Read one known entity state (TV is the preferred initial pilot).
7. List a limited domain such as `media_player`.
8. Inspect logs/history and confirm token never appears.

Do not add device-write calls until this read-only gate passes.
