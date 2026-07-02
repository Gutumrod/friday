---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-02-dispatch-to-hermes-implemented.md
วันที่: 2026-07-02
ผู้เขียน: Commander (Claude)
---

# Handoff — dispatch_to_hermes implemented (Phase 2 หัวใจ)

ต่อจาก [2026-07-02-github-init-and-timer-killprocess-verify.md](2026-07-02-github-init-and-timer-killprocess-verify.md) — เซสชันเดียวกัน ต่อเนื่องมาถึงตอนเย็น

## สรุป

Hermes contract แรก (`task_20260702_202827_...`) ได้คำตอบกลับมาแค่บรรทัดเดียว "ตอบแล้ว" ใช้ไม่ได้ — แก้โดยส่งรอบสองพร้อม `--deliverables` (บังคับ Hermes เขียนไฟล์จริงก่อน mark complete ได้ ดู [[reference-dispatch-hermes-openclaw]] ในเมมโมรี่) ได้คำตอบเต็มที่ `D:\AI-Workspace\shared\decisions\dispatch-to-hermes-contract-2026-07-02.md` (123 บรรทัด ครบ 4 หัวข้อ)

**เขียนโค้ด `dispatch_to_hermes` เสร็จแล้ว** ตาม contract นั้น (ยกเว้น 1 จุดที่ตัดออกโดยตั้งใจ — ดูด้านล่าง):

- `tool_dispatch_to_hermes(args)` — args format `"title|message"` (ตาม convention เดียวกับ `set_timer`) เรียก `mailbox_utils.py create ... --to Hermes` จริง (`subprocess.run`, `sys.executable`), parse `task_id` จาก stdout, แล้ว **blocking-poll** `results/hermes/<task_id>/result.json` (และ `errors/hermes/<task_id>/`) ทุก `DISPATCH_TO_HERMES_POLL_INTERVAL` (3s) จนกว่าจะเจอหรือครบ `DISPATCH_TO_HERMES_TIMEOUT` (300s default) — โครงเดียวกับ `tool_search_web`/`_execute_search_web`
- `status: completed` → คืน field `result` ตรงๆ (พูดให้ CEO ฟังได้เลยไม่ต้อง paraphrase), `status: blocked` → บอกว่า Hermes ขอข้อมูลเพิ่ม, `status: failed`/errors folder → บอก error, timeout → บอก task_id ไว้เช็คทีหลัง
- ผูกเข้า `TOOLS`, `TOOL_SCHEMAS` (title+message, required ทั้งคู่), `_pack_args` (เคสพิเศษเหมือน set_timer), **`CONFIRM_GATED`** (บังคับตาม contract ข้อ 1 — Friday confirm กับ CEO ก่อนเสมอ)
- แก้ system prompt (`build_system_prompt()`) — บรรทัดที่เคยบอกโมเดลว่า "สั่งงาน Hermes ยังทำไม่ได้ ให้ปฏิเสธ" เอาออก เปลี่ยนเป็นสอนให้เรียก `dispatch_to_hermes` แทนเมื่องานซับซ้อนเกินเครื่องมือที่มี (ไม่แก้จุดนี้ด้วยจะกลายเป็น bug จริง — โมเดลจะมี tool ให้เรียกแต่ system prompt สั่งให้ปฏิเสธไม่ใช้)

### ตัดออกโดยตั้งใจจาก contract: Hermes-side ACK/REJECT pre-check

Contract ข้อ 1 เสนอด่านยืนยันเพิ่มระหว่าง Friday↔Hermes เอง (ส่งสรุปสั้นๆ ให้ Hermes ACK/REJECT ก่อน ค่อย dispatch จริง) — **ไม่ทำใน v1** เหตุผล: task ที่มั่ว/ไม่ครบอยู่แล้วจะโผล่เป็น `blocked`/`failed` จาก Hermes เอง (safety net เดียวกัน แค่ช้ากว่าหนึ่ง round-trip) ไม่คุ้มที่จะเพิ่ม mailbox traffic เป็นสองเท่าทุกครั้งที่เรียก ถ้าเจอปัญหา task มั่วบ่อยจริงในทางปฏิบัติค่อยกลับมาเพิ่ม

## ทดสอบ

**53/53 passed** (51 เดิม + 2 ใหม่):
- `dispatch_to_hermes(polls result)` — mock `subprocess.run` + `MAILBOX_DIR` ชั่วคราว, seed `result.json` ปลอมไว้ล่วงหน้า, ยืนยันว่า flow create→parse task_id→poll→คืน field `result` ทำงานถูกทั้งสาย
- `dispatch_to_hermes(missing message rejected)` — args ที่ไม่มี "|message" ต้องถูกปฏิเสธ ไม่ยิง mailbox เปล่าๆ

**ยังไม่ได้ทดสอบแบบ real end-to-end** (เรียกจริงไปหา Hermes จริง) — CEO เลือกแค่ commit/push โค้ดไว้ก่อน รอวันที่อยู่หน้าเครื่องจริงพร้อมไมค์ค่อยทดสอบเต็มสาย (นี่คือ item เดิม "CEO ทดสอบพูดจริงผ่าน full voice pipeline" ที่ค้างมาตั้งแต่เช้า — ตอนนี้ทดสอบ dispatch_to_hermes จริงรวมอยู่ในนั้นด้วย)

## ค้างจากก่อนหน้า (ยังไม่เปลี่ยนสถานะ)

- **CEO ทดสอบพูดจริงผ่านไมค์** — ตอนนี้รวม `dispatch_to_hermes` เข้าไปด้วยแล้ว เป็น item ทดสอบใหญ่ที่สุดที่ค้างอยู่
- Test 2 (set_timer stress escalation) — ข้ามไว้ก่อนตามที่ CEO บอก
- Windows Thai SAPI voice — CEO ติดตั้ง language pack แล้ว รอรีสตาทเครื่อง ยังไม่ได้เช็ค/ตัดสินใจว่าจะโปรโมทเป็นเสียงหลักไหม
- Phase 3 (streaming), Phase 4 (VAD/wake word), Telegram integration — พักไว้เหมือนเดิม
- macOS porting (media_control, empty_recycle_bin, clipboard_*, set_timer's schtasks backup) — ยังไม่เริ่ม ไม่ใช่ priority ตอนนี้ (CEO ทำงานหลักที่เครื่อง Windows นี้ต่อ, Mac เป็นแค่ remote access point)

## ลงชื่อ

Commander (Claude) — session 2026-07-02
