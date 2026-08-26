# Phase 9 — Remote Command Security Contract

Date: 2026-08-26
Branch: `feat/phase9-remote-command-security-contract`
Parent: `feat/phase8-hermes-home-tool-intent-contract`
Status: **POLICY CONTRACT READY — NO PUBLIC NETWORK LISTENER ADDED**

## Goal

Prepare Friday to accept a future authenticated command from outside the home without exposing Home Assistant or Friday's side-effect executor directly to the public internet.

## Non-Negotiable Rules

- Remote transport must authenticate the caller before Friday policy evaluation.
- Home Assistant token never leaves the home-control integration layer.
- A remote request may stage a write action but cannot execute it with a one-shot `confirm=true` flag.
- Remote side effects require a separate confirmation proof bound to:
  - original request ID
  - authenticated subject
  - confirmation ID
- Friday's current `CONFIRM_GATED` remains authoritative.
- Remote command attempts require audit metadata.
- Audit records intentionally exclude tool arguments, HA tokens, bearer tokens, and response bodies.

## Implemented Contract

`src/friday/remote_command_policy.py` defines:

- command source (`local_voice`, `local_api`, `remote_api`)
- validated command context
- stage decision
- remote authentication requirement
- confirmation proof binding
- confirmed-execution authorization check
- minimal audit record builder

This module does not open a port, create a tunnel, or change the current Friday API routes.

## Security Property

An authenticated remote write request and its confirmation are two distinct steps. A captured/forged original request cannot self-authorize by carrying a safety-override field.

## Transport Decision Deferred

The secure transport mechanism is intentionally not hard-coded in Friday. When the owner is ready to enable outside-home access, choose and verify the actual authenticated transport/VPN/reverse-access design, then wire its trusted identity into `CommandContext`.

Do not expose port 8000 or Home Assistant port 8123 directly to the public internet as the implementation shortcut for this phase.
