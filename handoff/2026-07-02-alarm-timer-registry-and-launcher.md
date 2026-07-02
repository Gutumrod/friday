---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-02-alarm-timer-registry-and-launcher.md
วันที่: 2026-07-02
ผู้เขียน: Commander (Claude)
---

# Handoff — set_alarm/list_timers/cancel_timer, run_friday.bat

ต่อจาก [2026-07-02-dispatch-to-hermes-implemented.md](2026-07-02-dispatch-to-hermes-implemented.md) — เซสชันเดียวกัน ต่อเนื่องมา

## สรุป

CEO ถามว่าจะเพิ่มฟังก์ชันพื้นฐานอะไรให้ Friday ครบขึ้นก่อนดี — เสนอไปว่ารูโหว่ที่ชัดสุดคือ `set_timer` เดิม**ตั้งได้อย่างเดียว ไม่มีทางเช็ค/ยกเลิก** และ**ตั้งได้แค่นับถอยหลัง ไม่มีตั้งตามเวลานาฬิกา** CEO ให้ลองเลย ("นายลองเลย เดี๋ยวผมมา")

### สิ่งที่ทำ

- **Refactor:** ดึง logic กลาง (background thread + Task Scheduler backup) จาก `tool_set_timer` เดิมออกมาเป็น `_register_timer(seconds, message)` ใช้ร่วมกันได้
- **`tool_set_alarm(args)` ใหม่** — args `"HH:MM|message"` ตั้งเวลาตามนาฬิกา (ไม่ใช่นับถอยหลัง) เช่น "บอกตอน 3 ทุ่ม" → โมเดลต้องแปลงเป็น 24 ชม. เอง (`21:00`) ก่อนเรียก tool (สอนไว้ใน TOOL_SCHEMAS description) ถ้าเวลานั้นผ่านไปแล้ววันนี้ → เลื่อนไปพรุ่งนี้อัตโนมัติ
- **`_active_timers` registry ใหม่** — list ของ dict `{id, fire_at, message, task_name, cancel_event}` ป้องกัน race ด้วย `_timers_lock`
- **`tool_list_timers()` ใหม่** — read-only, ungated (Tier-0), แสดงรายการเรียงตามเวลาที่ใกล้ที่สุดก่อน พร้อมนาทีที่เหลือ
- **`tool_cancel_timer(args)` ใหม่** — ยกเลิกตามลำดับที่ (จาก list_timers), ตามคำในข้อความ, หรือเว้นว่าง=ยกเลิกทั้งหมด — CONFIRM_GATED (มีผลจริง)
- **Countdown เปลี่ยนจาก `time.sleep(seconds)` ยาวๆ เป็น poll `cancel_event.wait(timeout<=1s)` เป็นช่วงๆ** — ทำให้ cancel_timer แทรกกลางคันได้ ความแม่นยำเวลาที่เตือนจริงเหมือนเดิม (verify ด้วยเทสเดิม "returns immediately" ที่ไม่ได้แก้)
- **`run_friday.bat`** — launcher ดับเบิลคลิกได้ที่ root โปรเจกต์ เรียก python ของ conda env `friday` ตรงๆ (ไม่ผ่าน `conda activate` ที่บางทีมีปัญหาใน .bat) มี `pause` ท้ายสคริปต์กันหน้าต่างปิดถ้า error

### ทดสอบ

**56/56 passed** (53 เดิม + 3 ใหม่): invalid alarm time ถูกปฏิเสธ, alarm เลื่อนไปพรุ่งนี้ถ้าเวลาผ่านไปแล้ว, list→cancel หนึ่ง→cancel ที่เหลือ→ว่างเปล่า ครบวงจร — ทั้งหมด mock `_schedule_reminder_task`/`_cancel_reminder_task` (ของจริงมี live test แยกอยู่แล้ว `check_schedule_reminder_task_live`)

**ยังไม่ได้ทดสอบ end-to-end จริงผ่านเสียง** — พอดี CEO ออกไปกลางเซสชัน (ให้ลองเขียนเองก่อน) ทดสอบผ่าน automated suite ล้วน ยังไม่เรียกจริงผ่าน `main()`/ไมค์เลย

## ค้างจากก่อนหน้า (ไม่เปลี่ยนสถานะ)

เหมือน handoff ก่อนหน้าทั้งหมด (CEO ทดสอบไมค์จริง [ตอนนี้ครอบคลุม dispatch_to_hermes + set_alarm/list_timers/cancel_timer ด้วย], Test 2 stress, Windows Thai SAPI voice หลังรีสตาท, Phase 3/4, Telegram, macOS porting) — ไม่มีอะไรเปลี่ยนสถานะจากตัวนี้

## ลงชื่อ

Commander (Claude) — session 2026-07-02
