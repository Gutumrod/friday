# Friday for Hermes Multi-Agent Build Brief

วันที่: 2026-07-27
สถานะ: ready for new session
เจ้าของ review/merge: Codex
ขอบเขตเริ่มต้น: Phase 0 + Phase 1 Shadow Mode เท่านั้น

## Goal แรก

ทำให้ Friday repo มี Hermes Shadow Mode foundation ที่รันได้จริง โดยไม่เปลี่ยน UX เดิม ไม่ให้ Hermes execute tool และไม่แตะ Confirm Gate

ผลลัพธ์ที่ต้องได้ก่อนปิด Goal แรก:

- Friday สร้าง endpoint manifest จาก Hermes OpenAPI สดได้
- Friday ต่อ Hermes WebSocket `/api/ws` ด้วย flow `session.create` -> `prompt.submit` ได้
- Friday ส่ง text copy ไป Hermes แบบ background/fire-and-forget ได้
- Friday เก็บ shadow log พร้อม latency/correlation id ได้
- ถ้า Hermes ล่มหรือ timeout Friday ต้องยังทำงานปกติ
- Codex review diff และ approve ทีละขั้นก่อน commit/push

## Source Of Truth

อ่านไฟล์เหล่านี้ก่อนเริ่มงาน:

- `D:\AI-Workspace\projects\friday\docs\FRIDAY_FOR_HERMES_BUILD_PLAN_2026-07-27.md`
- `D:\AI-Workspace\projects\friday\docs\FRIDAY_FOR_HERMES_PLAN_2026-07-26.md`
- `D:\AI-Workspace\runtime\hermes-native\workspace\hermes-dashboard-api-for-friday.md`
- `D:\AI-Workspace\projects\friday\AGENTS.md`

ถ้าข้อมูลใน chat ขัดกับไฟล์ ให้ยึดไฟล์ก่อน แล้วค่อยรายงานความต่างให้ Codex ตัดสิน

## Operating Model

Codex เป็นคนคุมงานหลัก:

- แตก task
- ตรวจ source of truth
- review code
- รวมงาน
- รัน test gate
- approve phase
- ตัดสินใจ commit/push

Hermes ใช้เป็นตัวช่วยงานเล็กและงาน probe:

- ตรวจ endpoint contract
- ยืนยัน WebSocket message flow
- ทดลอง prompt routing
- สรุปผล latency/behavior
- ช่วยอ่านข้อความหรือ log แล้วสรุป

Claude ใช้กับงานใหญ่หรือ reasoning หนัก:

- review architecture
- ตรวจ risk ของ concurrency/timeout/context
- review diff ใหญ่
- ช่วยออกแบบ test matrix
- วิเคราะห์ bug ที่ต้องไล่หลายไฟล์

ห้ามให้ Hermes หรือ Claude เป็น approval gate สุดท้าย

## Phase Boundary

### Phase 0: Probe + Manifest

เป้าหมาย:

- ยืนยันว่า Friday เรียก Hermes dashboard ได้จากเครื่องจริง
- สร้าง endpoint manifest จาก OpenAPI สด
- แยก `/api/ws` เป็น manual runtime route เพราะไม่อยู่ใน OpenAPI
- เก็บ evidence แบบไม่ log token/secrets

งานที่ Codex ทำ:

- อ่าน repo จริง
- เช็ค `git remote -v`
- ถ้ามี remote ให้ `git fetch --all`
- ตรวจ branch/worktree ก่อนแก้
- เพิ่มหรือแก้ไฟล์ตาม pattern เดิม
- ทำ probe command ที่ reproduce ได้

งานที่ส่ง Hermes ได้:

- ถามว่า OpenAPI path ล่าสุดมี endpoint อะไรบ้าง
- ถาม WebSocket event flow ล่าสุด
- ให้ Hermes ตอบเฉพาะ contract/evidence ไม่ให้แก้ repo Friday

งานที่ส่ง Claude ได้:

- ถ้า endpoint manifest design กระทบหลาย module
- ถ้าเลือก abstraction แล้วมี risk ว่าจะผูก Friday กับ Hermes แน่นเกินไป

Acceptance:

- `/api/health` probe ได้เมื่อ dashboard เปิด
- `/api/status`, `/api/model/info`, `/api/cron/jobs`, `/openapi.json` probe ได้พร้อม auth ถ้าจำเป็น
- dashboard down แล้ว error ต้อง graceful
- ไม่มี token/secrets ใน log

### Phase 1: Shadow Mode

เป้าหมาย:

- Friday ทำงานเหมือนเดิมทุกอย่าง
- เพิ่ม pipeline ส่ง user text copy ไป Hermes แบบ background
- Hermes response ใช้เพื่อ log/compare เท่านั้น ยังไม่เอามาพูด

งานที่ Codex ทำ:

- เพิ่ม config `FRIDAY_FOR_HERMES_MODE=off|shadow`
- default ต้องเป็น `off`
- เพิ่ม `HERMES_DASHBOARD_URL=http://127.0.0.1:9119`
- เพิ่ม timeout/keepalive config ตามแผน
- เพิ่ม `hermes_client.py` หรือ module ที่ตรงกับ pattern repo
- ต่อ WebSocket `/api/ws`
- ส่ง `session.create` -> `prompt.submit`
- ทำ fire-and-forget task หลัง STT โดยไม่ block voice loop
- เขียน shadow log ที่ `vault/hermes_shadow/YYYY-MM-DD.jsonl`

งานที่ส่ง Hermes ได้:

- ทดลอง prompt packet สั้นๆ เพื่อดู response/latency
- ช่วยสรุป response quality เทียบกับ intent ของ user
- ยืนยัน error event ที่ WebSocket อาจส่งกลับ

งานที่ส่ง Claude ได้:

- review concurrency model
- review timeout/cancellation behavior
- review ว่า shadow task ไม่ block voice loop จริงไหม

Acceptance:

- `FRIDAY_FOR_HERMES_MODE=off` behavior เดิมต้องไม่เปลี่ยน
- `FRIDAY_FOR_HERMES_MODE=shadow` ต้อง log ได้ แต่ห้ามพูด/ใช้ผล Hermes
- Hermes timeout หรือล่มแล้ว Friday ยังตอบได้
- shadow log มี `correlation_id`, `mode`, `status`, `hermes_ttfb_ms`, `hermes_total_latency_ms`, `error`
- test gate ผ่าน

## Task Routing Rules

ส่ง Hermes เมื่อ:

- งานใช้เวลาไม่เกิน 5-10 นาที
- เป็นการ probe/ถาม contract/สรุป evidence
- ไม่มีการแก้ repo Friday
- ไม่มี secret
- ไม่มี side effect
- คำตอบเอามาให้ Codex ตรวจต่อได้

ส่ง Claude เมื่อ:

- งานต้องอ่านหลายไฟล์และคิด architecture
- งานเกี่ยวกับ concurrency, async lifecycle, cancellation, restart recovery
- งานต้อง review diff ใหญ่
- งานต้องออกแบบ test matrix
- งานที่พลาดแล้วอาจทำให้ voice loop ค้างหรือ safety gate หลุด

ให้ Codex ทำเองเมื่อ:

- แก้ไฟล์ใน Friday repo
- เพิ่ม config/env
- เขียน test
- รวม diff
- รัน test gate
- ตัดสินใจ approve phase
- commit/push

## Hermes Prompt Template

ใช้เมื่ออยากให้ Hermes ช่วยงานเล็ก:

```text
You are Hermes helping Friday for Hermes Phase 0/1.

Scope:
- Do not modify Friday repo.
- Do not execute tools.
- Do not request secrets.
- Return concise technical findings only.

Source:
- Friday repo: D:\AI-Workspace\projects\friday
- Hermes dashboard: http://127.0.0.1:9119
- Phase: <Phase 0 Probe | Phase 1 Shadow>

Task:
<specific small task>

Return:
- verified
- uncertain
- failed
- recommended next action for Codex
```

## Claude Prompt Template

ใช้เมื่ออยากให้ Claude ช่วยงานใหญ่:

```text
You are reviewing Friday for Hermes Phase 0/1 as an architecture reviewer.

Do not implement unless explicitly asked.
Focus on:
- voice loop safety
- async non-blocking behavior
- timeout/cancellation
- logging without secrets
- confirm gate isolation
- minimal blast radius

Source files or diff:
<paste paths or diff summary>

Return:
- blocking risks
- non-blocking concerns
- missing tests
- suggested smallest fix
```

## Codex Review Checklist

ก่อน approve แต่ละ step:

- อ่าน diff จริง
- ตรวจว่าไม่มี unrelated refactor
- ตรวจว่า default mode ยัง `off`
- ตรวจว่า token ไม่ถูก log
- ตรวจว่า shadow mode ไม่เปลี่ยน UX
- ตรวจว่า Hermes failure ไม่ทำให้ Friday failure
- ตรวจว่าไม่มี Hermes tool execution
- ตรวจว่า Confirm Gate ไม่ถูกแตะ
- รัน test gate
- เขียนสรุปผลลง handoff หรือ audit

## Test Gate

รันจาก repo root:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\core.py src\friday\config.py src\friday\hermes_client.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py
```

ถ้าแตะ UI/API เพิ่ม:

```powershell
cd D:\AI-Workspace\projects\friday\ui
npm run build
```

## Stop Lines

หยุดและขอ approval ก่อนทำสิ่งเหล่านี้:

- เปิด `sync` mode
- ให้ Hermes response ถูกพูดออกเสียงจริง
- ให้ Hermes ส่ง `tool_intent`
- ให้ Friday execute tool จาก Hermes intent
- แตะ Confirm Gate
- ใช้ Hermes filesystem/git write
- สร้าง Kanban task ผ่าน Hermes
- เปลี่ยน voice loop หลัก
- commit/push หลัง implementation

## Final Report Format

เมื่อทำเสร็จ ให้ session ใหม่ส่งรายงานแบบนี้:

```text
Friday for Hermes Phase 0/1 Report

Changed files:
- ...

Implemented:
- ...

Hermes delegated tasks:
- ...

Claude delegated tasks:
- ...

Commands run:
- ...

Results:
- ...

Risks / uncertain:
- ...

Codex approval needed:
- ...
```

## First Step For New Session

1. เปิดไฟล์นี้
2. เปิด build plan
3. เช็ค `git status --short`
4. เช็ค `git remote -v`
5. ถ้ามี remote ให้ `git fetch --all`
6. อ่านไฟล์จริงก่อนแก้
7. เริ่ม Phase 0 Probe + Manifest ก่อน ห้ามข้ามไป Shadow Mode ทันที
