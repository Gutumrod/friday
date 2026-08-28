# LG TV Integration Record — 2026-08-28

**Repository:** `Gutumrod/friday`  
**Device:** LG webOS TV  
**Purpose:** Live exploration evidence for Friday integration workflow  
**Status:** Direct webOS/WoL control works; reliability fixes required before productionizing the direct path

## Connection / Discovery

- Wake-on-LAN uses the known TV MAC and UDP broadcast on port 9.
- Direct control uses LG webOS over TCP/WebSocket on port 3001 with the existing paired client key.
- Friday local config still pointed to `192.168.1.107` during this test.
- The TV was actually reachable at `192.168.1.128` and matched the known TV MAC in ARP.
- This confirms DHCP/IP drift is a real failure mode for the current direct path.

## Live Test Evidence

1. TV was initially offline/unreachable through Friday's configured IP.
2. `tool_tv_power('on')` sent the Wake-on-LAN packet successfully.
3. Friday's delayed verification reported failure because `_tv_connect()` still used the stale configured IP.
4. Network discovery/ARP found the TV at `192.168.1.128`.
5. Direct webOS connection to `192.168.1.128` succeeded.
6. YouTube search resolved: `คืนท้าผี • คุณคิม | 1 ส.ค. 69 | THE GHOST RADIO`.
7. `tool_tv_play_video(...)` successfully deep-linked the selected video into the TV's YouTube app after overriding the IP only for the live test session.
8. Read-back confirmed current app id `youtube.leanback.v4`.
9. `tool_tv_power('off')` succeeded.
10. A follow-up connection attempt failed as expected, confirming the TV had powered off.

## Read Capabilities Proven

- TV reachability / offline state
- current foreground app id
- installed app list through webOS

## Write Capabilities Proven

- Wake-on-LAN power on
- webOS power off
- app launch
- YouTube deep-link playback
- remote/input controls through the existing direct webOS path

## Issues / Required Fixes

### P0 — Remove stale-IP dependency from the direct TV path

Current failure: Wake-on-LAN turned the TV on, but Friday immediately concluded that startup failed because verification tried the stale configured IP.

Required behavior:

- Prefer Home Assistant entity addressing once Phase 4 is live.
- While the direct webOS compatibility path remains, resolve/re-discover the TV by stable identity (MAC/device discovery) instead of trusting one static IP forever.
- A DHCP reservation may be used as a transition aid, but the Friday intent layer must not depend on raw IP.

### P0 — Make Wake-on-LAN verification use the resolved live endpoint

Current `_verify_tv_on()` calls `_tv_connect()` using `TV_IP` only.

Required behavior:

- Verify against the current resolved endpoint or Home Assistant entity state.
- Do not report Wake-on-LAN failure solely because the configured IP is stale.
- Keep verification bounded and fail clearly if the TV truly remains unavailable.

### P1 — Add power-on → boot-ready → playback orchestration

The owner request was a single semantic action: open the TV and play a YouTube episode.

Current tools required separate power-on and playback steps during this test.

Required behavior:

- A logical media action should be able to wake the TV when needed, wait for readiness using bounded verification, then launch/play media.
- The full side-effect path must remain under Friday confirmation/policy rules.
- Do not duplicate vendor-specific sequencing in the intent layer; normalize it behind the TV/media adapter or Home Assistant path.

### P1 — Track authoritative state vs last-known media title

Confirmed current app can be read from webOS, but this test did not prove authoritative playback-title metadata from the TV.

Required behavior:

- Prefer live Home Assistant/media-player metadata when available.
- Otherwise use Friday's media-session record only as last-known commanded media.
- Never answer an exact current YouTube title from memory as if it were live state.

### P1 — Harden YouTube lookup runtime dependencies

During live `yt-dlp` search, warnings showed:

- no supported JavaScript runtime detected
- `ffmpeg` not found

The current search still worked because Friday only needed metadata/video id, but the JavaScript-runtime warning is a future reliability risk as YouTube extraction changes.

Required behavior:

- Provide/configure a supported JS runtime for `yt-dlp` in the Friday environment.
- Decide whether `ffmpeg` is actually required for Friday's metadata-only search path; if not, document it as optional rather than adding an unnecessary dependency.
- Add a regression check that YouTube search resolves a video id without interactive/browser fallback.

### P1 — Rotate the LG webOS paired client key

The current development plan already records that the old client key existed in public repository history.

Required behavior:

- Re-pair/rotate the TV client key before treating the direct path as production-safe.
- Keep the new key only in machine-local secret/config storage.

## Production Path Decision

Canonical target remains:

```text
Friday / Hermes
 -> logical intent + Friday safety policy
 -> Home Assistant
 -> LG webOS TV entity
```

Direct webOS + Wake-on-LAN remains a compatibility/rollback path until Home Assistant parity is proven.

## Acceptance Criteria for the Next TV Gate

- TV can be powered on from a fully-off state without relying on a stale hard-coded IP.
- Friday verifies the TV actually became reachable/available.
- One semantic request can wake the TV and start selected YouTube media without manual intervention.
- Current app/source state can be read back after the command.
- Power off can be issued and offline state verified.
- No device credential or paired key is stored in source.
- Failure messages distinguish: WoL failure, discovery/IP failure, pairing/auth failure, app-launch failure, and media-search failure.
