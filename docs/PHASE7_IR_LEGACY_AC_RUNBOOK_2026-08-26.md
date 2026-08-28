# Phase 7 — Legacy AC via IR / Home Assistant Runbook

Date: 2026-08-26
Branch: `feat/phase7-ir-legacy-ac-readiness`
Parent: `feat/phase6-smart-home-confirm-gated-tools`
Status: **HARDWARE/HA SETUP READY — NO FRIDAY PRODUCTION CODE CHANGE REQUIRED YET**

## Architecture Rule

Friday must not learn/send raw IR codes itself.

Target:

`Friday semantic tool -> Home Assistant logical climate/device layer -> IR remote integration -> AC`

Friday should continue to operate on logical state such as:

- device: `downstairs_ac`
- power: `on`
- temperature: `25`
- mode: `cool`
- fan: `auto`

## Verified Home Assistant Capability (2026-08-26)

Home Assistant's official Broadlink integration supports RM-family universal remotes including RM4 Mini and creates remote/infrared entities for supported IR devices. Learned IR commands can be captured with `remote.learn_command` and later transmitted with `remote.send_command`.

Important: Broadlink's built-in `climate` entities are for supported thermostats, not a generic arbitrary IR air-conditioner abstraction. Therefore do not assume an old AC automatically appears as `climate.*` just because an RM4 Mini is paired.

## Pilot Hardware Sequence

1. Use one IR blaster in the downstairs AC room first.
2. Add the IR device to Wi-Fi using the manufacturer setup path required by the integration.
3. Add/discover the IR integration in Home Assistant.
4. Confirm the HA `remote.*`/`infrared.*` entity is available.
5. From Home Assistant Tools > Actions, learn/send one harmless command first.
6. Learn/verify AC state commands needed by the real remote.
7. Determine the correct HA abstraction for this exact AC:
   - preferred: a supported integration that exposes a real `climate.*` entity
   - acceptable pilot: HA scripts/scenes representing full desired AC states
   - do not make Friday store raw IR payloads
8. Only after HA can reliably reproduce the desired state should `home_devices.json` map `downstairs_ac` to the resulting entity/script control contract.

## AC State Caveat

Many AC remotes transmit a complete state packet, so a learned command may represent a full state (power/temp/mode/fan) rather than a simple incremental button press.

Physical remote use can make software-assumed state drift because IR is generally one-way. If HA cannot read true AC state:

- mark state as assumed/uncertain in the integration design
- do not tell the user a physical state was verified when it was only commanded
- optional later improvement: independent room-temperature/current sensing

## Safety

- Do not use a cheap low-current smart plug as the AC power-control path.
- Do not expose raw IR learning/sending as a general LLM tool.
- Keep real-world actions behind Friday Confirm Gate.
- First pilot is one AC, one room, one IR device.
- Expand upstairs only after the downstairs command/state model is stable.

## Hardware Gate

This phase cannot be marked PASS until the IR device is physically installed and one real AC completes:

- power on/off
- 25 C state
- cool mode
- fan mode if supported
- repeated command reliability test
- physical-remote state-drift test

No merge requirement should depend on a guessed AC model or unverified IR code library.
