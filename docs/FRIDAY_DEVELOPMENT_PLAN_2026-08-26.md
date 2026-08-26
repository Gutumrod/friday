# Friday Development Plan — Voice + Home Assistant Roadmap

วันที่: 2026-08-26
repo: `Gutumrod/friday`
branch: `master`

## Goal

พัฒนา Friday ให้เป็น voice front-door ของบ้านและระบบ agent โดยคง Friday เป็น safety gateway + local tool executor และให้ Hermes เป็น reasoning/worker router ตาม architecture เดิม

Target flow ระยะยาว:

`Mic -> Streaming STT -> Friday -> Hermes/LLM -> Validated Tool Intent -> Confirm Gate -> Home Assistant -> Device -> Result -> Friday TTS`

หลักสำคัญ:

- Friday เป็นผู้ execute side-effect tools
- Hermes ห้ามสั่งอุปกรณ์จริงตรง
- Home Assistant เป็น smart-home control plane กลาง
- Friday ไม่ผูกกับยี่ห้ออุปกรณ์ เช่น Broadlink/Tuya/LG โดยตรงใน business intent layer
- STT ต้องเปลี่ยน provider ได้และ benchmark จากเสียงจริงก่อนเลือก
- ทุก real-world side effect ต้องผ่าน policy/Confirm Gate ตามกติกา repo
- ห้าม hard-code credentials, tokens, client keys, IP-specific secrets ใน source

---

## Current Verified Baseline

### Voice / STT

Current production path:

`Microphone -> SpeechRecognition -> Google Cloud STT (th-TH) -> recognize_google fallback`

ข้อจำกัดปัจจุบัน:

- `r.listen()` รอประโยคจบก่อน transcribe
- `phrase_time_limit=15`
- ยังไม่มี provider abstraction
- ยังไม่ได้ใช้ true streaming ASR

### LLM / Tool Routing

- Ollama native structured function calling ใช้งานแล้ว
- `TOOLS` + `TOOL_SCHEMAS` เป็น execution boundary
- `CONFIRM_GATED` เป็น safety boundary ของ side effects
- TV tools มี live precedent แล้ว: power, volume, app launch, video, remote button

### Friday API/UI

มี FastAPI service boundary แล้ว:

- `/api/chat`
- `/api/tools`
- `/api/tool/confirm`
- `/ws/events`

ดังนั้นไม่สร้าง control panel/CLI architecture ใหม่จากศูนย์ ให้ reuse Friday API + tool layer เดิม

### Hermes

Architecture เดิมยังคงใช้:

`off -> shadow -> sync -> tool_intent`

Friday ยังเป็น safety executor และ Hermes เป็น reasoning/worker router

---

# Phase 0 — Security & Machine-Specific Config Cleanup

Status: **BLOCKER BEFORE SMART-HOME EXPANSION**

## Scope

- ย้าย LG TV client key ออกจาก `config.py`
- ย้าย device-specific values ที่ควรเป็น runtime config ไป env/config layer
- เพิ่ม validation ตอน startup สำหรับ required secrets
- ไม่ log secret/token/raw credential
- document secret rotation / re-pair procedure

ค่าที่ต้อง review:

- `TV_CLIENT_KEY`
- device IP/MAC ที่ควร configurable
- Home Assistant token ในอนาคต
- cloud/STT credentials path

## Acceptance

- source ไม่มี credential/token จริง
- `.env.example` มีเฉพาะ placeholder
- missing/invalid secret fail clearly พร้อม logging ที่ไม่ leak secret
- TV control regression ผ่าน
- user re-pair/rotate key ที่เคยอยู่ใน public history ถ้าจำเป็น

Gate: **Owner approval required before Phase 1 implementation**

---

# Phase 1 — STT Provider Abstraction

Status: PLANNED

## Goal

แยก speech recognition ออกจาก `core.py` เพื่อให้สลับ provider ได้โดยไม่แก้ voice loop หลัก

## Target structure

- `src/friday/stt/base.py`
- `src/friday/stt/google.py`
- `src/friday/stt/typhoon.py`
- `src/friday/stt/factory.py`

Suggested contract:

- `transcribe(audio) -> STTResult`
- provider name
- text
- confidence/quality metadata ถ้ามี
- latency_ms
- error classification

Config:

- `FRIDAY_STT_PROVIDER=google|typhoon`
- provider-specific settings ผ่าน env
- fallback policy explicit ไม่ silent

## Acceptance

- Google behavior เดิมยังทำงานเหมือนเดิม
- provider สลับได้โดย config
- hard failure / unclear speech แยกประเภทได้
- latency logging ระบุ provider
- unit tests ครอบ provider selection + failure path

---

# Phase 2 — Thai STT Benchmark: Google vs Typhoon ASR Real-Time

Status: PLANNED

## Goal

เลือก STT จาก evidence ของเสียงเจ้าของจริง ไม่เลือกจาก benchmark vendor อย่างเดียว

## Dataset

อัดอย่างน้อย 30 utterances แบ่งเป็น:

1. ภาษาไทยทั่วไป
2. ไทยปนอังกฤษ
3. ชื่อแอป/เทคโนโลยี เช่น YouTube, Home Assistant, Friday, Hermes
4. คำสั่งบ้าน เช่น เปิดทีวี ปรับเสียง เปิดแอร์ 25 องศา
5. ประโยคพูดเร็ว/เว้นจังหวะธรรมชาติ
6. background noise ระดับใช้งานจริง

## Measure

- transcription correctness
- command-critical error rate
- latency median/p95
- Thai-English code-switch accuracy
- number/date/temperature handling
- CPU/GPU/RAM usage

## Decision rule

Typhoon ผ่านสำหรับ production เมื่อ:

- command-critical accuracy >= current Google baseline
- latency ดีกว่าอย่างมีนัยสำคัญ
- error behavior predictable
- local runtime stable บน hardware ปัจจุบัน

ถ้าไม่ผ่าน: Google remains default, Typhoon stays experimental

---

# Phase 3 — Streaming Voice Pipeline

Status: BLOCKED BY PHASE 2

## Goal

ใช้ข้อดีของ realtime ASR จริง แทนการอัดจนจบประโยคก่อนส่ง

Target:

`Mic audio chunks -> streaming ASR -> partial transcript -> endpoint/final transcript -> Friday intent pipeline`

## Scope

- streaming microphone reader
- partial/final transcript state
- interruption-safe audio locks
- barge-in rules เพื่อไม่ให้ Friday ฟังเสียงตัวเอง
- endpoint detection
- timeout/fallback behavior
- preserve current turn-based mode as rollback option

## Acceptance

- first partial transcript เร็วกว่าปัจจุบันชัดเจน
- final command ไม่โดนตัดกลางคำ
- TTS ไม่ bleed เข้า STT
- rollback ไป legacy turn-based STT ได้ด้วย config
- latency evidence before/after

---

# Phase 4 — Home Assistant Foundation

Status: PLANNED; IMPLEMENT ONLY AFTER OWNER APPROVAL

## Goal

ใช้ Home Assistant เป็น smart-home control plane กลาง

Friday ต้องไม่คุยกับ IR blaster/plug/smart TV vendor โดยตรงใน intent layer

Target flow:

`Friday Tool -> HomeAssistantClient -> HA REST/WebSocket API -> Entity/Service`

## Target module

`src/friday/home_assistant_client.py`

Responsibilities:

- authenticated local API client
- health check
- entity state read
- service call
- timeout/retry policy
- structured error mapping
- no secret logging

Config via env:

- `HOME_ASSISTANT_URL`
- `HOME_ASSISTANT_TOKEN`
- `HOME_ASSISTANT_CONNECT_TIMEOUT`

## Initial read-only tools

- `ha_status`
- `ha_get_entity_state`
- `ha_list_entities` (filtered/limited)

## Acceptance

- Friday can probe HA health
- Friday can read one known entity state
- failure does not block voice loop indefinitely
- no token appears in log/history

---

# Phase 5 — Home Device Registry & Stable Aliases

Status: BLOCKED BY PHASE 4

## Goal

ไม่ให้ LLM/Hermes ต้องรู้ raw entity IDs, IP, MAC หรือ vendor details

Example logical registry:

- `living_room_tv`
- `downstairs_ac`
- `upstairs_ac`
- `bedroom_fan`

Each logical device maps to Home Assistant entities/capabilities

## Rules

- aliases config-driven
- support Thai aliases เช่น `แอร์ล่าง`, `ทีวีห้องนั่งเล่น`
- entity allowlist
- capability validation before execute
- unknown/ambiguous device => ask/return structured error, never guess

---

# Phase 6 — Smart Home Tool Set

Status: BLOCKED BY PHASE 5

## Initial tools

### Climate

- `home_ac_power`
- `home_ac_set_temperature`
- `home_ac_set_mode`
- `home_ac_set_fan_mode`
- `home_ac_set_state`

### General

- `home_device_power`
- `home_scene_activate`
- `home_device_status`

All write tools are side effects and must be registered in `CONFIRM_GATED` unless a later explicit safety policy defines a narrower safe exception.

## AC state model

Friday/Hermes communicates desired semantic state:

```text
power=on
temperature=25
mode=cool
fan=auto
```

Home Assistant/device integration handles vendor-specific IR/service details

Friday must not implement raw IR code logic

---

# Phase 7 — IR Blaster / Legacy AC Integration

Status: HARDWARE-DEPENDENT FUTURE PHASE

## Goal

เพิ่มแอร์เก่าผ่าน IR blaster โดยให้ HA expose เป็น climate/device entity

Rules:

- one IR blaster may control multiple IR devices in same physical coverage area
- remote เดิมยังใช้งานได้
- acknowledge state-desync risk when physical remote is used
- prefer HA climate abstraction over raw button emulation
- if true device state is unavailable, mark state as assumed/uncertain

## First pilot

- ชั้นล่าง 1 IR blaster
- 1 AC only first
- validate power + temperature + mode
- after stable, expand to upstairs

---

# Phase 8 — Hermes Tool Intent Bridge for Home Control

Status: BLOCKED BY EXISTING HERMES SPEAK-ONLY SYNC + TOOL_INTENT GATES

## Goal

Hermes may reason about smart-home intent but Friday remains validator/executor

Flow:

`Hermes tool_intent -> Friday schema validation -> entity/capability validation -> Confirm Gate -> Friday HA tool -> result`

Negative cases required:

- unknown tool
- malformed args
- out-of-range temperature
- unknown device alias
- HA unavailable
- timeout
- confirmation denied
- duplicated/replayed command

Hermes must never receive raw HA token

---

# Phase 9 — Remote From Outside Home

Status: FUTURE

Goal example:

> “Friday กำลังกลับบ้าน เปิดแอร์ล่าง 25 องศา”

Security requirements:

- do not expose Home Assistant unauthenticated to public internet
- use approved secure remote path/VPN/reverse access design
- authentication + authorization required
- audit every remote side-effect command
- optional stronger confirmation for remote execution

---

# Phase 10 — Automation / Iron-Man Layer

Status: FUTURE

Examples:

- `กำลังกลับบ้าน` scene
- arrival pre-cooling
- bedtime scene
- away mode
- energy-aware automation
- sensor-triggered actions

Important:

Automation policy belongs in Home Assistant where practical; Friday is conversational orchestration, not the only runtime for house automations.

This ensures automations keep working even if Friday/Hermes/LLM is offline.

---

# Engineering Rules For All Phases

1. View current code before editing
2. One phase at a time
3. Owner approves phase before implementation
4. Production-ready changes only; no throwaway snippets in production path
5. Error handling + structured logging required
6. No hard-coded credentials
7. Tests required for positive + negative paths
8. Real device changes must respect Confirm Gate
9. Keep rollback path for STT and HA integration
10. Commit/push every approved checkpoint per repo workflow
11. Do not let Hermes bypass Friday safety/tool validation
12. Do not couple semantic commands to vendor hardware

---

# Recommended Execution Order

1. **Phase 0 — Security cleanup**
2. **Phase 1 — STT provider abstraction**
3. **Phase 2 — Google vs Typhoon real benchmark**
4. **Phase 3 — streaming STT only if benchmark supports it**
5. Continue existing Hermes evidence/sync gates in parallel where safe
6. **Phase 4 — Home Assistant read-only foundation**
7. **Phase 5 — device registry**
8. **Phase 6 — smart-home tools**
9. **Phase 7 — IR AC pilot after hardware arrives**
10. Hermes tool-intent bridge only after its existing safety gates pass

---

# Current Stop Line

This document is planning only.

Do **not** implement yet without owner approval:

- secret/config migration
- STT provider changes
- Typhoon runtime integration
- streaming microphone changes
- Home Assistant client
- new smart-home tools
- Confirm Gate changes
- Hermes live tool execution

Next implementation phase when approved: **Phase 0 — Security & Machine-Specific Config Cleanup**
