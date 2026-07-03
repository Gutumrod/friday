# n8n "FRIDAY Mailbox Notifier" — สถานะ + วิธีใช้ (2026-07-03)

เอกสารสรุปงานแก้ n8n workflow ที่ทำทั้งวันนี้ (คู่กับ `handoff/2026-07-03-a1-verify-closed-dispatch-bugs-found.md`
และห้องคุย `mailbox/room/claude-hermes.md`) — เขียนเป็น reference แยกเพื่อไม่ต้องไล่อ่าน handoff/room ยาวๆ อีกรอบ

## สถานะรวม ณ ตอนนี้

✅ **ฝั่งรับ (n8n → Telegram) ทำงานสมบูรณ์แล้ว** — เทสผ่านหลายรอบติดต่อกัน
❌ **ฝั่งส่ง (Friday) ยังไม่มี** — Friday ยังไม่มีโค้ดเขียนไฟล์เข้า inbox เลย ดูหัวข้อ "ช่องว่างที่เหลือ" ด้านล่าง

---

## Architecture

```
[Schedule Trigger ทุก 5 นาที]
        ↓
[HTTP GET http://dstack-n8n:8899/list]     ← list ไฟล์ใน mailbox/inbox/hermes/
        ↓
[Code node: ถ้าว่าง → return [] จบเลย]
        ↓
[Telegram: ส่ง "📥 FRIDAY: <ชื่อไฟล์>"]
        ↓
[HTTP POST http://dstack-n8n:8899/move]    ← ย้ายไฟล์ที่เจอไป mailbox/notified/
```

### Container topology (จุดสำคัญที่เคยพลาด)

n8n รันแบบ **queue mode** — มี container แยก 2 ตัว:
- `dstack-n8n` — main/scheduler, รัน `inbox_poll.js` (server พอร์ต 8899) ด้วย
- `dstack-n8n-worker` — execute node จริงทุกตัวผ่าน Redis queue

**เพราะแยก container กัน HTTP node ในทั้งสองจุดต้องเรียก `http://dstack-n8n:8899/...`
(ใช้ docker network alias) ห้ามใช้ `localhost` หรือ `127.0.0.1` เด็ดขาด** — จาก `dstack-n8n-worker`
(ที่ node จริงรันอยู่) คำสองคำนั้นหมายถึง loopback ของ worker เอง ไม่ใช่ของ `dstack-n8n` ที่ server
รันอยู่ ผลคือ `ECONNREFUSED` ทุกรอบ (เจอมาแล้ววันนี้)

### `inbox_poll.js` (server ที่ 8899)

- อยู่ที่ `/mailbox/inbox_poll.js` ในคอนเทนเนอร์ `dstack-n8n`
- อ่าน/ย้ายไฟล์จาก `/mailbox/inbox/hermes` → `/mailbox/notified` (mount มาจาก
  `D:\AI-Workspace\mailbox\inbox\hermes` และ `D:\AI-Workspace\mailbox\notified` บนเครื่องจริง)
- **Persistent ผ่าน restart แล้ว** — สตาร์ทเองตอน container boot ผ่าน custom entrypoint:
  - `D:\AI-Stack\n8n\docker-entrypoint.sh` (รัน `nohup node /mailbox/inbox_poll.js` ก่อน `exec n8n`)
  - mount เข้า image ผ่าน `D:\AI-Stack\n8n\docker-compose.yml`
  - ทดสอบจริงแล้ว: `docker restart dstack-n8n` → workflow auto-activate + `inbox_poll.js` กลับมาเอง

### Workflow ใน n8n

- ชื่อ: **FRIDAY Mailbox Notifier**
- id: `Lqfyc8SoWbY1IrIv`
- `active: true`

---

## ผลการทดสอบวันนี้

| เวลา (UTC) | Execution ID | ผล |
|---|---|---|
| 12:15–12:25 | 5376–5378 | ❌ error (URL ยังเป็น `127.0.0.1`) |
| 12:30 | 5379 | ✅ success — ไฟล์ทดสอบย้ายไป `notified/` จริง |
| 12:30–13:10 | 5379–5387 | ✅ success ติดต่อกัน 9 รอบ |
| หลัง `docker restart dstack-n8n` | — | ✅ workflow + `inbox_poll.js` กลับมาเองครบ ไม่ต้องแก้มือ |

ไฟล์ทดสอบที่ใช้: `test_final_1783077404.md` (สร้างด้วยมือ ไม่ใช่ Friday สร้าง — ดูช่องว่างด้านล่าง)

---

## วิธีทดสอบเอง

1. สร้างไฟล์อะไรก็ได้ (แม้ว่างเปล่า) ที่ `D:\AI-Workspace\mailbox\inbox\hermes\<ชื่ออะไรก็ได้>.md`
2. รอไม่เกิน 5 นาที (schedule trigger รอบถัดไป)
3. เช็คผล 2 ทาง:
   - **Telegram** ควรเห็นข้อความ `📥 FRIDAY: <ชื่อไฟล์>`
   - **ไฟล์ควรย้ายไป** `D:\AI-Workspace\mailbox\notified\`

## วิธีเช็คสถานะ/debug

**ผ่าน n8n UI:** `http://localhost:5678` (user: `admin`, pass: `cbl_admin_pass`) → Executions →
"FRIDAY Mailbox Notifier"

**ผ่าน DB ตรง (เร็วกว่า ไม่ต้องเปิดเว็บ):**
```bash
docker exec dstack-postgres psql -U n8n -d n8n -c \
  "SELECT id, mode, \"startedAt\", status FROM execution_entity \
   WHERE \"workflowId\"='Lqfyc8SoWbY1IrIv' ORDER BY \"startedAt\" DESC LIMIT 5;"
```

**เช็คว่า `inbox_poll.js` ยังรันอยู่ไหม:**
```bash
docker exec dstack-n8n sh -c "ps aux | grep inbox_poll"
docker exec dstack-n8n-worker sh -c "wget -qO- http://dstack-n8n:8899/list"
```

---

## ช่องว่างที่เหลือ (ยังไม่ได้ทำ)

**Friday (`friday_walkie_talkie.py`) ยังไม่มีโค้ดเขียนไฟล์เข้า `mailbox/inbox/hermes/` เลย**

Tool ที่มีอยู่ตอนนี้คือ `tool_dispatch_to_hermes` (บรรทัด 813) ซึ่งเป็นคนละกลไก — เรียก
`mailbox_utils.py create --to Hermes` แล้ว **block รอผลจาก `results/hermes/<task_id>/`**
(กลไกเก่าที่มีปัญหาเรื่อง Hermes crash + เงียบระหว่างรอ ที่ pipeline ใหม่นี้ตั้งใจจะเลี่ยง)

ต้องเพิ่ม tool ใหม่ใน Friday ที่แค่เขียนไฟล์ธรรมดาลง `mailbox/inbox/hermes/<ชื่อ>.md` แล้วจบ
(fire-and-forget ไม่ block) ถึงจะใช้ pipeline นี้ได้จริงจากปาก Friday — ยังไม่ได้ implement

---

## อัปเดต 2026-07-03 (เย็น) — ฝั่งส่งทำเสร็จแล้ว + เจอบั๊กใหม่ฝั่งรับ

✅ **ฝั่งส่ง (Friday) เสร็จแล้ว** — เพิ่ม `tool_notify_hermes(args)` ใน `friday_walkie_talkie.py`
เขียนไฟล์ลง `mailbox/inbox/hermes/<timestamp>-<hex>-<sanitized message>.md` (fire-and-forget,
CONFIRM_GATED เหมือนเครื่องมืออื่นที่มีผลจริง) ทดสอบเต็ม flow แล้วจริง: คำสั่งธรรมชาติ
("บอก Hermes...ไม่ต้องรอตอบกลับนะ") → Friday (gemma4:31b-cloud) เลือก `notify_hermes` ถูกต้อง
(แยกจาก `dispatch_to_hermes` ที่ยังเก็บไว้คู่กันสำหรับงานที่ต้องรอผลจริง) → ยืนยัน → เขียนไฟล์จริง
→ n8n poll เจอ → **Telegram แจ้งเตือนจริง 2/2 ครั้ง**

❌ **บั๊กใหม่ที่เจอจากการทดสอบจริง: Telegram Markdown parse_mode กิน `_`/`*`/`` ` ``/`[` ทิ้ง**

ไฟล์จริงบนดิสก์ชื่อถูกต้องครบ (เช่น `20260703_205633_7c970b_ทดสอบ...tool_notify_hermes.md`)
แต่ข้อความที่ขึ้นใน Telegram **ตัวอักขระ `_` หายไปทุกตัว** (เช่น
`202607032056337c970bทดสอบ...toolnotifyhermes.md`) — ยืนยันซ้ำ 2/2 ครั้ง ไม่ใช่ครั้งเดียว

**สาเหตุ:** n8n ส่งข้อความเข้า Telegram node โดยเปิด Markdown parse_mode แต่ไม่ escape อักขระพิเศษ
ก่อนส่ง — Telegram ตีความ `_..._` เป็น italic แล้วลบตัว `_` ทิ้งตอน render ผลกระทบไม่ได้จำกัดแค่
`_` เท่านั้น ข้อความที่มี `*`/`` ` ``/`[` ก็มีความเสี่ยงโดนตีความ/หายแบบเดียวกัน

**แก้ชั่วคราวฝั่ง Friday แล้ว (2026-07-03):** เปลี่ยนตัวคั่นในชื่อไฟล์ที่ Friday สร้างเองจาก `_`
เป็น `-` (ไม่ใช่ Markdown special char) และ sanitize ข้อความส่วนที่ผู้ใช้พูดเองด้วย regex เดียวกัน
ก่อนใส่ในชื่อไฟล์ — แก้ได้แค่ "ฝั่งสร้างชื่อไฟล์" เท่านั้น

**ยังไม่ได้แก้ (งานของ Hermes/n8n):** ต้นเหตุจริงคือฝั่ง n8n Telegram node เอง ถ้าจะแก้ให้ครบต้อง
เลือกทางใดทางหนึ่ง:
1. Escape อักขระพิเศษ Markdown (`_`, `*`, `` ` ``, `[`, `]`) ก่อนส่งเข้า Telegram node หรือ
2. ปิด parse_mode ของ Telegram node ไปเลย (ส่งเป็น plain text ไม่ต้องตีความ Markdown)

ยังจำเป็นอยู่แม้ฝั่ง Friday จะ sanitize ชื่อไฟล์ที่ตัวเองสร้างแล้ว เพราะข้อความที่ผู้ใช้พูดเองอาจมี
อักขระพิเศษเหล่านี้ปนมาได้เสมอ (ตัวอย่างการทดสอบนี้ sanitize ไปแล้วเลยไม่โดน แต่ข้อความในอนาคตที่
ไม่ผ่าน Friday อาจโดน)
