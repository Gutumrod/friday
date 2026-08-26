# Friday Phase 5 Home Device Registry Handoff

Date: 2026-08-26
Branch: `feat/phase5-home-device-registry`
Parent: `feat/phase4-home-assistant-foundation`
Status: CODE READY / REAL ENTITY MAPPING PENDING

Friday can now reason using logical device names/Thai aliases while Home Assistant entity IDs stay in a local ignored registry.

Next branch may implement write tools, but all such tools must:

- resolve through this registry
- require the declared capability
- never accept arbitrary raw entity IDs from the LLM
- be added to `CONFIRM_GATED`
- use Home Assistant service calls, not state-representation writes
- remain unmerged until Phase 4/5 live read-only verification succeeds
