# Home Network Device Inventory — 2026-08-28

**Repository:** `Gutumrod/friday`  
**Purpose:** Confirmed device inventory for Friday smart-home exploration  
**Scope:** Home LAN observations and owner-confirmed identities only

## Confirmed Devices

### Friday Host PC
- IP observed: `192.168.1.112`
- Role: Windows PC used as Friday runtime / exploration bench
- Status during scan: online

### Home Router / Gateway
- IP observed: `192.168.1.1`
- MAC observed: `F8-79-28-C3-34-9E`
- Role: default gateway for the `192.168.1.x` LAN

### LG webOS TV
- Previously observed live IP: `192.168.1.128`
- Previous stale Friday config IP: `192.168.1.107`
- Identity: confirmed LG webOS TV
- Notes: IP changed under DHCP; direct control must not depend on a permanently hard-coded IP
- Related evidence: `docs/LG_TV_INTEGRATION_RECORD_2026-08-28.md`

### Indoor Security Camera
- IP observed: `192.168.1.103`
- MAC observed: `54-AF-97-45-2D-C2`
- Identity: owner-confirmed indoor security camera
- Vendor family evidence: TP-Link / Tapo-compatible network identity
- Reachability: responds to ICMP ping; TTL observed `64`
- Read-only service discovery during scan:
  - TCP `443` open
  - TCP `8443` open
  - TLS certificate on `443`: `CN=TPRI-DEVICE, O=TPRI`
- NetBIOS hostname: not exposed
- PTR hostname: not exposed
- Control/integration status: not yet tested

## Friday Integration Rules

- Device identity must be based on confirmed logical identity, not IP address alone.
- IP addresses in this file are observations and may change under DHCP.
- Discovery/probing remains read-only until a specific integration test is intentionally started.
- Do not store device passwords, session cookies, tokens, pairing keys, or other credentials in this inventory.
- Future production control should prefer Home Assistant or another deterministic local protocol rather than brittle UI automation.

## Next Discovery Candidates

For the security camera, future exploration may check, without changing device state:
- Home Assistant/Tapo integration compatibility
- ONVIF support
- RTSP support
- local authenticated API availability
- whether camera state, privacy mode, motion events, or stream availability can be represented as logical Friday capabilities

No write/control action against the camera has been performed as of this record.
