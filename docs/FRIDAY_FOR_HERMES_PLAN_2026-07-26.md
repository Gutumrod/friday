# Friday for Hermes Plan

วันที่: 2026-07-26
สถานะ: accepted product direction, implementation not started
เจ้าของงาน: Friday + Hermes integration

## Product Name

ชื่อที่เลือก: **Friday for Hermes**

เหตุผล:

- ชัดว่า Friday เป็น voice layer ให้ Hermes ไม่ใช่ agent คู่แข่งอีกตัว
- จำง่ายสำหรับผู้ใช้ Hermes เดิม
- วางตำแหน่งได้ตรง: ติดตั้งแล้ว Hermes มีหู มีปาก และมี confirm gate ผ่านเสียง

## Product Intent

Friday for Hermes คือ voice front-end สำหรับคนใช้ Hermes

เป้าหมายคือให้ผู้ใช้ไม่ต้องพิมพ์ prompt, นั่งรอ, และอ่าน output ตลอดเวลา แต่พูดสั่ง Hermes ได้เหมือนคุยกับผู้ช่วย โดยมี Friday เป็นตัวกลางที่รับเสียง พูดกลับ จัด routing และคุม safety ของเครื่องผู้ใช้

ไม่ใช่การเอา Hermes มาแทน Friday และไม่ใช่การทิ้ง mailbox หรือ confirm gate เดิม

## Role Split

| Component | Role | Rule |
|---|---|---|
| Friday | Voice Runtime + Safety Gateway | รับเสียง, พูดกลับ, validate, confirm, execute local Friday tools |
| Hermes | Reasoning/Worker Router | วิเคราะห์ intent, เลือก route, ใช้ Hermes tools, ส่ง tool intent หรือ async job result |
| Mailbox | Async Job Queue | งานหนัก งานยาว งานที่ไม่ควร block voice loop |
| Ollama | Model Backend | LLM engine ที่อาจถูกเรียกจาก Friday เดิมหรือผ่าน Hermes ตาม mode |

## Operating Modes

ใช้ feature flag เพื่อไม่รื้อของเดิมทีเดียว:

| Mode | Behavior | Use |
|---|---|---|
| `off` | Friday ใช้ flow เดิมทั้งหมด | default stable path |
| `shadow` | Friday ตอบเองเหมือนเดิม แต่ส่งสำเนา text ไป Hermes เพื่อดู Hermes routing decision | เก็บ evidence โดยไม่กระทบผู้ใช้ |
| `sync` | Friday ส่งบาง intent ไป Hermes แบบ realtime ตาม routing policy | MVP ใช้งานจริงแบบคุมความเสี่ยง |
| `async_only` | Friday ใช้ Hermes เฉพาะงาน mailbox/background | fallback สำหรับเครื่องที่ไม่พร้อม direct sync |

ค่า config ที่เสนอ:

- `FRIDAY_FOR_HERMES_MODE=off|shadow|sync|async_only`
- `HERMES_SYNC_URL=http://127.0.0.1:<port>`
- `HERMES_KEEPALIVE_INTERVAL_SECONDS=5`
- `HERMES_KEEPALIVE_MAX_COUNT=4`
- `HERMES_SYNC_SOFT_DETACH_SECONDS=20`
- `HERMES_SYNC_HARD_TIMEOUT_SECONDS=60`
- `FRIDAY_CORRELATION_ID_PREFIX=ffh`

## Three-Track Routing

### Track 1: Fast Track

Friday จัดการเองเพื่อรักษา latency ต่ำ

ใช้กับ:

- คำสั่ง deterministic ที่ Friday มี tool พร้อมแล้ว
- read-only local status เช่น `get_time`, `disk_space`, `system_status`, `network_status`, `list_processes`, `list_timers`
- phrase/status สั้น ๆ ที่ไม่ต้องใช้ reasoning ลึก
- confirm/cancel path ที่เกี่ยวกับ pending tool

กฎ:

- ไม่ต้องส่ง Hermes ถ้าคำตอบได้เร็วและปลอดภัยอยู่แล้ว
- ห้ามเพิ่ม progress phrase ให้ fast tool ถ้าไม่มี latency evidence ว่าผู้ใช้รอจริง

### Track 2: Sync Delegation

Friday ขอให้ Hermes ช่วยแบบ realtime เมื่อ Friday ไม่มี tool หรือ Hermes เหมาะกว่า

ใช้กับ:

- weather/current external facts
- short research
- external service ที่ Hermes มี tool/MCP พร้อมกว่า
- routing หรือ planning สั้น ๆ ที่ต้องตอบผู้ใช้ทันที

กฎ:

- อย่าใช้ hard timeout 2-5 วินาทีกับงาน Hermes ปกติ เพราะ model ใหญ่อาจคิด 20-30 วินาที
- ใช้ progressive keep-alive แล้ว auto-detach เป็น async background ถ้านานเกิน soft detach window
- ใช้ timeout สั้นเฉพาะ connect/network failure ไม่ใช่ normal thinking time
- Hermes ส่งกลับได้ 2 ชนิดเท่านั้น:
  - `speak`: ข้อความให้ Friday พูด
  - `tool_intent`: ข้อเสนอให้ใช้ Friday tool แต่ยังไม่ execute

### Track 3: Async Job

Friday ส่งงานลง mailbox เมื่อเป็นงานหนักหรืองานยาว

ใช้กับ:

- ตรวจ repo/projekt
- เขียนหรือแก้หลายไฟล์
- research ยาว
- งานที่ต้องรอ agent worker ทำจริง
- งานที่ควรมี artifact/report แยก

กฎ:

- voice loop ไม่ควร block รอจนงานเสร็จ
- Friday ต้องพูดรับงานพร้อม task id/correlation id แบบสั้น
- Hermes/bridge ต้องเขียน result กลับให้ poll/notify ได้
- mailbox ยังเป็น durable source of truth สำหรับ async work

## Safety Contract

Friday ถือกุญแจ safety เสมอ

- Hermes ห้าม execute Friday local tools ตรง
- Hermes ส่งได้แค่ `tool_intent`
- Friday validate tool name, schema, args, and allowlist เอง
- Friday ตัดสินเองว่า tool นั้น gated หรือ ungated
- gated tools ต้องใช้ confirm gate ของ Friday ก่อน execute
- ทุก side-effect tool ต้องอยู่ใน `CONFIRM_GATED`
- confirm reject ต้อง log raw STT text, stripped text, pending tool, and correlation id
- negative confirmations เช่น `ไม่`, `ไม่เอา`, `ไม่ใช่` ต้องชนะ confirm words เสมอ

## Tool Intent Validation & Retry Policy

Hermes is LLM-backed, so `tool_intent` can be malformed even when the contract says it should be structured. Friday must treat every Hermes tool intent as untrusted input.

Validation rules:

- reject unknown tool names
- reject missing required args
- reject args that do not match `TOOL_SCHEMAS`
- reject side-effect tools that are not represented in `CONFIRM_GATED`
- reject any request that tries to bypass Friday confirmation
- never guess a "close enough" tool name automatically

Retry behavior:

- `MAX_TOOL_INTENT_RETRIES=2`
- on validation failure, Friday sends a structured `schema_error` back to Hermes with:
  - `correlation_id`
  - `tool`
  - `error_code`
  - `message`
  - `expected_schema` or schema version
  - `retry_count`
- Hermes may return a corrected `tool_intent`
- if retries are exhausted, Friday cancels the command and says:
  - "ข้อมูลเครื่องมือไม่ถูกต้อง ขอยกเลิกคำสั่งก่อนนะคะ"

This retry loop belongs to Phase 3 before any Hermes-sourced `tool_intent` is allowed to execute.

## Logging / Audit

ทุก request ต้องมี `correlation_id`

Minimum fields:

- `correlation_id`
- `mode`
- `route`: `fast_track`, `sync_delegation`, `async_job`, `fallback`
- `user_text`
- `stt_confidence` ถ้ามี
- `hermes_request_started_at`
- `hermes_latency_ms`
- `hermes_response_type`
- `tool_intent`
- `confirm_required`
- `confirm_result`
- `tool_executed`
- `fallback_reason`
- `final_spoken_text`
- `hermes_ttfb_ms`
- `hermes_total_latency_ms`
- `keepalive_count`
- `soft_detach`
- `hard_timeout`
- `schema_retry_count`
- `result_delivered_after_restart`

Friday ต้องยังเก็บ transcript/voice history ของตัวเอง ไม่ย้าย history ไป Hermes อย่างเดียว

## Telemetry & Environment Secrets

All integration config must come from environment variables or a local secret/config file that is not committed.

Required config/secrets policy:

- no hard-coded Hermes URL
- no hard-coded API keys
- no hard-coded database/service credentials
- no hard-coded user-specific external service tokens
- `.env.example` should document required keys without real values when implementation starts
- local-only defaults should bind to `127.0.0.1` unless explicitly configured otherwise

Required telemetry:

- Hermes TTFB: time from request sent to first byte/event/response chunk
- Hermes total latency
- route decision latency
- keep-alive count
- soft detach and hard timeout flags
- fallback reason
- schema validation retry count
- mailbox result delivery latency
- whether the result was delivered after Friday restart

Telemetry must be structured and must not log secret values.

## Graceful Degradation & Fallback UX

Friday must never go silent or read raw stack traces when Hermes/Ollama/backend tools fail.

Minimum failure classes:

- Hermes unreachable
- Hermes invalid response
- Hermes hard timeout
- Ollama unavailable/OOM behind Hermes
- schema/tool intent invalid
- mailbox unavailable
- result store unavailable

Fallback behavior:

- direct Hermes failure -> Friday current stable flow when possible
- direct Hermes failure for long work -> enqueue async mailbox job when possible
- mailbox failure -> tell the user background handoff is unavailable
- invalid tool intent after retry exhaustion -> cancel the command safely

User-facing fallback phrase:

- "ไม่สามารถเชื่อมต่อสมองหลักได้ในขณะนี้ ขอสลับเป็นระบบสำรองนะคะ"

The spoken message should be short and human-readable; detailed exception data belongs in logs only.

## Context Window Policy

Hermes also has a context window because its backend is still an LLM, currently expected to be
`deepseek-v4-flash:cloud` through Ollama for Hermes-side reasoning. Friday for Hermes must not
assume Hermes can remember unlimited spoken history.

Design rule:

- Friday keeps the full local transcript/audit trail.
- Hermes receives only the minimum context needed for the current route.
- Sync delegation should send an intent packet, not the whole voice transcript.
- Async jobs should receive a compact task brief and source paths, not an accumulated chat dump.
- Long-running Hermes work should keep its own task-local artifact under mailbox/results, not rely on live chat memory.

Recommended payload budgets:

| Route | Context Sent To Hermes | Budget Rule |
|---|---|---|
| Fast Track | none unless shadow mode is enabled | 0 live dependency |
| Shadow | current user text + small route metadata | no transcript history |
| Sync Delegation | current user text + 3-5 stable facts + relevant tool/result snippets | target under 2k tokens |
| Tool Intent | current user text + allowed Friday tool schemas or schema version | do not resend all schemas every turn if versioned |
| Async Job | standalone task brief + paths + acceptance criteria | target under 4k tokens unless explicitly needed |

Required safeguards:

- Add `context_budget_tokens` to Friday -> Hermes requests.
- Add `context_policy` to logs: `minimal`, `recent_turns`, `task_brief`, or `full_debug`.
- Default must be `minimal`.
- `full_debug` is manual/debug-only and must not be the normal voice path.
- If Hermes says it needs more context, it should ask Friday for a specific artifact/path, not request full transcript by default.
- Before public packaging, add a context-pressure test with a long voice session to verify Sync Delegation still sends bounded payloads.

This avoids the failure mode where Hermes looks smarter at first, then slowly gets worse because the voice layer keeps stuffing old conversation into the model window.

## Context Pruning Strategy

When payloads exceed the chosen `context_budget_tokens`, Friday should prune by priority, not by raw FIFO alone.

Never prune:

- system/safety policy
- current user utterance
- current route/mode
- current `correlation_id`
- pending confirm state
- current task brief
- core state needed for safety or execution
- relevant artifact paths

Prune first:

- old chat turns
- repeated keep-alive/status events
- verbose tool output that already has a saved artifact path
- raw transcript segments that have already been summarized
- stale route decisions unrelated to the current request

Recommended packet shape:

```text
System + Safety + Core State
+ Current User Request
+ Current Pending Job/Confirm
+ Recent 3-5 Turns
+ Summarized Older Context
+ Relevant Artifact Paths
```

This keeps Friday's safety identity stable while still fitting Hermes's model window.

## Voice UX & Progressive Handoff Policy

Hermes can take longer than a normal voice assistant turn. Live observation from direct Hermes use:

- larger-model ordinary work often takes around 20-30 seconds
- longer work can take around 60 seconds

Therefore Friday for Hermes should not use a hard 2-5 second cutoff for every Sync Delegation request. The voice UX needs a progressive handoff so the user does not sit in dead air, while the voice loop also does not stay blocked forever.

### Progressive Async Handoff

Recommended default flow:

1. Friday sends the request to Hermes with a `correlation_id`.
2. Friday immediately speaks a short neutral acknowledgement:
   - "ส่งให้ Hermes ตรวจสอบให้นะคะ"
3. While waiting, Friday may speak keep-alive phrases every 5 seconds, up to 3-4 times:
   - "Hermes กำลังทำอยู่นะคะ"
   - "น่าจะกำลังคิดงานอยู่ รอสักครู่นะคะ"
   - "ยังรอผลจาก Hermes อยู่นะคะ"
4. If Hermes still has not returned after the keep-alive window, roughly 20 seconds by default, Friday auto-detaches:
   - "ดูเหมือนจะใช้เวลาคิดนาน เดี๋ยว Friday คุยเป็นเพื่อนไปก่อนนะคะ ถ้าเสร็จแล้วเดี๋ยวมาบอก"
5. The pending Hermes request becomes an async background job.
6. Friday returns to normal voice mode immediately.
7. When Hermes returns a result, Friday announces it later at a safe moment.

### Timing Defaults

| Setting | Default | Notes |
|---|---:|---|
| `HERMES_KEEPALIVE_INTERVAL_SECONDS` | 5 | delay between spoken keep-alives |
| `HERMES_KEEPALIVE_MAX_COUNT` | 4 | about 20 seconds before detach |
| `HERMES_SYNC_SOFT_DETACH_SECONDS` | 20 | switch from waiting to background |
| `HERMES_SYNC_HARD_TIMEOUT_SECONDS` | 60 | stop waiting on the direct connection, but do not cancel the Hermes work |

The earlier 2-5 second timeout remains useful only for low-level network/connect failures, not for normal Hermes thinking time.

### Durable Result Fallback

Hard timeout must not mean lost work.

If a Sync Delegation request crosses `HERMES_SYNC_HARD_TIMEOUT_SECONDS`, Friday should stop waiting on the direct HTTP/WebSocket path, but Hermes should keep the job alive and persist the eventual result through the async channel.

Required behavior:

1. Friday sends every Hermes request with a durable `correlation_id`.
2. Hermes creates or records a durable job entry before doing substantial work.
3. If Friday disconnects, hard-times-out, or closes, Hermes continues processing when possible.
4. When Hermes finishes after the direct connection is gone, Hermes writes the result to mailbox/results or the agreed async result store using the same `correlation_id`.
5. Friday, when running, polls or subscribes to pending result notifications and announces completed work at a safe idle moment.
6. If Friday is not running, the result remains durable and is announced on next startup or visible through mailbox/status tooling.

This turns a long Sync Delegation into an Async Job automatically without losing the work already done.

Implementation note:

- `HERMES_SYNC_HARD_TIMEOUT_SECONDS` is a Friday foreground-wait limit, not a Hermes cancellation timeout.
- If Hermes cannot keep processing after client disconnect due to its server architecture, it must explicitly enqueue the task into mailbox before returning/closing.
- Friday should keep a small local `pending_hermes_jobs` registry under ignored runtime state so it can reconcile unfinished jobs on startup.
- The registry should store only metadata: `correlation_id`, route, created_at, last_status, mailbox task id/result path if known, and short user-facing title.

### Return Notification

When Hermes finishes after detach:

- Friday should not interrupt while `mic_listening` is active.
- Friday should not speak over current audio playback.
- Friday should queue the result notification and play it at the next idle moment.
- Friday startup should check pending Hermes jobs from the local registry and mailbox result store.
- If a result arrived while Friday was closed, Friday should announce a compact catch-up:
  - "Hermes ทำงานที่ค้างไว้เสร็จแล้วค่ะ ให้สรุปให้ฟังไหมคะ"
- The notification should be short first, then offer more detail:
  - "Hermes ทำงานนั้นเสร็จแล้วค่ะ ให้สรุปให้ฟังไหมคะ"
- Long results should be summarized before TTS; full artifacts stay in mailbox/results.

### Safety Rules For Keep-Alive Speech

- keep-alive phrases must not imply success before Hermes returns a result
- keep-alive phrases must not trigger confirm gate or stand in for a confirmation question
- keep-alive phrase audio should come from the phrase bank when possible
- if the user speaks during a wait, user speech wins and Friday should stop waiting in the foreground
- detached jobs must remain queryable by `correlation_id` or task id
- direct timeout must never discard a Hermes result silently

### Result Read Interrupt

Full barge-in is not required for the MVP, but Friday should support a narrow interrupt path for long async result playback.

MVP behavior:

- applies only while Friday is reading a long completed Hermes result
- detect short stop commands such as "หยุด", "พอ", "เดี๋ยวก่อน", "พักก่อน"
- stop TTS playback
- store read position by `correlation_id`
- return to listening mode
- allow the user to resume or ask for a shorter summary later

Non-goal for MVP:

- full-duplex conversation while Hermes is thinking
- interrupting confirm prompts
- interrupting gated execution

## Minimal Protocol Draft

Friday -> Hermes:

```json
{
  "type": "user_input",
  "correlation_id": "ffh_20260726_001",
  "mode": "sync",
  "text": "เช็คอากาศวันนี้ให้หน่อย",
  "context_budget_tokens": 2000,
  "context_policy": "minimal",
  "context": {
    "source": "voice",
    "capabilities": ["speak", "tool_intent", "async_job"],
    "friday_tools_version": "local"
  }
}
```

Hermes -> Friday speak:

```json
{
  "type": "speak",
  "correlation_id": "ffh_20260726_001",
  "text": "วันนี้กรุงเทพอากาศร้อน มีโอกาสฝนช่วงเย็นค่ะ"
}
```

Hermes -> Friday tool intent:

```json
{
  "type": "tool_intent",
  "correlation_id": "ffh_20260726_002",
  "tool": "open_app",
  "args": {"name": "notepad"},
  "reason": "ผู้ใช้ขอเปิดแอปบนเครื่อง Windows"
}
```

Friday -> Hermes tool result:

```json
{
  "type": "tool_result",
  "correlation_id": "ffh_20260726_002",
  "tool": "open_app",
  "confirmed": true,
  "executed": true,
  "result": "เปิด notepad ให้แล้วค่ะ"
}
```

## Implementation Phases

### Phase 0: Contract + Live Capability Probe

Status: not started

Work:

- verify current Hermes gateway endpoint/port
- verify whether direct REST endpoint exists today
- document exact endpoint and auth/local-only boundary
- confirm mailbox bridge health and result path
- record current Hermes model/backend and any configured context length
- decide first-pass `context_budget_tokens` for each route
- document required environment variables and `.env.example` shape
- define baseline telemetry fields and log destinations
- define graceful degradation messages for Hermes/Ollama/mailbox failure
- add contract doc/test fixtures only, no runtime behavior change

Acceptance:

- one command proves Hermes direct sync path exists or is missing
- one command proves mailbox async path health
- one note records the verified model/context source or says it is not discoverable yet
- one fixture covers context pruning priority
- one fixture covers graceful degradation response shape
- no Friday behavior change

### Phase 1: Shadow Mode

Status: not started

Work:

- add feature flag `FRIDAY_FOR_HERMES_MODE=shadow`
- after Friday STT text, send non-blocking shadow request to Hermes
- do not use Hermes response for user-facing answer
- log Hermes route decision and latency
- log approximate payload size/context policy for every shadow request
- log Hermes TTFB/total latency when available

Acceptance:

- Friday behaves exactly like current stable mode
- shadow logs show Hermes decision for at least 20 real utterances
- shadow payloads stay within the chosen context budget
- no secrets appear in logs
- no confirm-gate regression

### Phase 2: Sync Delegation MVP

Status: not started

Work:

- enable sync delegation for a small allowlist of intent classes
- start with non-side-effect, non-local tools only
- use progressive keep-alive before auto-detach instead of a short hard cutoff
- fallback to Friday current flow only for connect errors or hard timeout
- Hermes can return `speak` only in first sync MVP
- implement graceful fallback voice UX for Hermes/Ollama unavailable

Acceptance:

- voice user can ask one Hermes-backed realtime question
- normal 20-30 second Hermes thinking does not create dead air
- auto-detach returns Friday to normal voice mode if Hermes takes too long
- transcript includes correlation id and fallback reason
- Hermes failure speaks a short fallback message and does not expose stack traces

### Phase 3: Tool Intent Bridge

Status: not started

Work:

- allow Hermes to return `tool_intent`
- Friday validates intent against `TOOL_SCHEMAS`
- Friday sends structured `schema_error` back to Hermes on validation failure
- Friday allows at most `MAX_TOOL_INTENT_RETRIES=2`
- Friday applies existing `CONFIRM_GATED`
- Friday executes only after confirm when required
- Friday sends result back to Hermes

Acceptance:

- one ungated tool intent works
- one gated tool intent asks confirm and only executes after confirm
- negative confirm cancels
- tests cover schema rejection, unknown tool, retry exhaustion, gated tool, and timeout

### Phase 4: Async Job UX

Status: not started

Work:

- polish mailbox handoff for long jobs
- Friday speaks short acknowledgement with task id
- add status query by correlation id/task id
- keep result report in mailbox
- support result-read interrupt for long spoken summaries

Acceptance:

- long task does not block voice loop
- user can ask status later
- Hermes result can be summarized by Friday
- user can stop a long result readout without losing the result

### Phase 5: Packaging For Hermes Users

Status: not started

Work:

- installer/run docs for Hermes users
- minimal config template
- Windows-first setup
- local-only security defaults
- troubleshooting guide

Acceptance:

- fresh Hermes user can run Friday for Hermes locally
- no Google Drive build/install path requirement
- no generated runtime files committed

## First Implementation Recommendation

Start with Phase 0 + Phase 1 only.

Do not start with full direct-connect tool execution. The useful first question is not "can Hermes replace Friday's brain?" but:

- Can Friday send spoken text to Hermes without hurting the current voice loop?
- Can Hermes produce a better routing decision than Friday's current LLM path?
- Can we measure latency and reliability before using Hermes output live?

## Explicit Non-Goals For MVP

- no wake word
- no full-duplex/barge-in
- no replacing current Friday stable flow
- no removing mailbox
- no moving confirm gate to Hermes
- no Hermes direct execution of Friday local tools
- no public packaging before local PoC passes
