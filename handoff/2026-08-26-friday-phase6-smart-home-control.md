# Friday Phase 6 Smart-Home Control Handoff

Date: 2026-08-26
Branch: `feat/phase6-smart-home-confirm-gated-tools`
Parent: `feat/phase5-home-device-registry`
Status: CODE READY / DO NOT MERGE BEFORE LIVE READ-ONLY GATES

Write path is now implemented behind Friday's existing Confirm Gate and logical device registry.

Important:

- Do not bypass confirmation for convenience.
- Do not let Hermes call Home Assistant directly.
- Do not accept arbitrary entity IDs from LLM output.
- Keep temperature and mode validation before service calls.
- First real write pilot should be TV power or another reversible, visible action before AC/IR.

Phase 7 is hardware/integration work for legacy AC via an HA-supported IR remote. Friday should continue to see a climate-like logical device, not raw IR codes.
