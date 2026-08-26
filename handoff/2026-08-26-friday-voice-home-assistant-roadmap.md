# Friday Voice + Home Assistant Roadmap Handoff

วันที่: 2026-08-26
repo: `Gutumrod/friday`
branch: `master`

## What Changed

Planning only. No production code was changed.

Added:

- `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`

The new plan extends the existing Friday/Hermes architecture toward:

- replaceable STT providers
- evidence-based Google vs Typhoon ASR comparison
- optional true streaming ASR
- Home Assistant as the smart-home control plane
- semantic device aliases instead of vendor/IP/MAC coupling
- legacy AC control through Home Assistant + IR blaster
- Hermes tool intent only through Friday validation + Confirm Gate

## Verified Current Architecture

Current Friday runtime remains:

`Mic -> Google Cloud STT -> Ollama native tool calling -> Friday tool layer -> Confirm Gate -> executor -> TTS`

Friday already has:

- `TOOLS`
- `TOOL_SCHEMAS`
- `CONFIRM_GATED`
- LG webOS TV tools
- FastAPI service boundary (`/api/chat`, `/api/tools`, `/api/tool/confirm`, `/ws/events`)
- Hermes shadow client foundation

Therefore Home Assistant should be integrated as a Friday tool/integration layer, not directly into Hermes or the STT layer.

## Important Finding

`src/friday/config.py` currently contains machine-specific LG webOS configuration including a client key in source.

The repository is public, so secret/config cleanup is now Phase 0 and must happen before introducing Home Assistant tokens or further smart-home credentials.

Do not add any new secret/token directly to source.

## New Phase Order

1. Phase 0 — Security & machine-specific config cleanup
2. Phase 1 — STT provider abstraction
3. Phase 2 — Google vs Typhoon ASR benchmark using real owner speech
4. Phase 3 — true streaming voice pipeline only if benchmark supports it
5. Phase 4 — Home Assistant read-only foundation
6. Phase 5 — logical device registry / Thai aliases
7. Phase 6 — smart-home tools + Confirm Gate
8. Phase 7 — IR blaster legacy AC pilot
9. Phase 8 — Hermes tool-intent bridge for home control
10. Phase 9 — secure remote-from-outside-home path
11. Phase 10 — automation / scene layer

## Architecture Decision

Long-term control flow:

`Mic -> STT -> Friday -> Hermes/LLM -> validated intent -> Friday Confirm Gate -> Home Assistant -> device`

Rules:

- Friday stays the safety gateway and executor.
- Hermes can reason/suggest but must not bypass Friday tool validation.
- Home Assistant owns device/vendor integration and persistent household automations.
- Friday communicates semantic desired state, e.g. `downstairs_ac / on / 25C / cool / auto`.
- Raw IR codes and vendor details stay below Friday's semantic tool layer.

## Stop Line

Do not implement any of the following until the owner explicitly approves the next phase:

- config/secret migration
- Typhoon integration
- STT runtime replacement
- streaming microphone changes
- Home Assistant client
- smart-home write tools
- Confirm Gate changes
- Hermes live tool execution

Next approved implementation target should be:

**Phase 0 — Security & Machine-Specific Config Cleanup**

## Files To Read Next

1. `AGENTS.md`
2. `handoff/2026-08-26-friday-voice-home-assistant-roadmap.md`
3. `docs/FRIDAY_DEVELOPMENT_PLAN_2026-08-26.md`
4. `handoff/2026-07-28-friday-development-plan-refresh.md`
5. `docs/FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`
6. `docs/VOICE_LATENCY_ROADMAP_2026-07-19.md`
