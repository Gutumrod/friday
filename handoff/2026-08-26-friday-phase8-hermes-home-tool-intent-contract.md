# Friday Phase 8 Hermes Home Tool-Intent Handoff

Date: 2026-08-26
Branch: `feat/phase8-hermes-home-tool-intent-contract`
Parent: `feat/phase6-smart-home-confirm-gated-tools`
Status: VALIDATION CONTRACT READY / LIVE HERMES EXECUTION BLOCKED

The branch prepares strict validation only. It does not wire Hermes output to Friday execution.

Before live use, the existing Hermes speak-only sync gate must pass. Then the live bridge must feed validated intents back through Friday's normal pending-confirm flow rather than calling `CONFIRM_GATED[tool]["execute"]` directly.
