# Friday Phase 4 Home Assistant Foundation Handoff

Date: 2026-08-26
Branch: `feat/phase4-home-assistant-foundation`
Parent: `feat/phase1-stt-provider-abstraction`
Status: READ-ONLY CODE READY / LIVE HA PENDING

## Safety Boundary

This branch has no Home Assistant device-control service calls. It reads status/entity state only.

If `HOME_ASSISTANT_URL` or `HOME_ASSISTANT_TOKEN` is missing, the runtime does not register HA tools and Friday continues without them.

## Next

Phase 5 can build a logical device registry/Thai alias layer on top of this client without controlling anything.

Phase 6 write tools must not start until the real read-only HA gate passes; every write tool must be confirm-gated.
