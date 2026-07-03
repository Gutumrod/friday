---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-03-a1-verify-closed-dispatch-bugs-found.md
วันที่: 2026-07-03
ผู้เขียน: Commander (Claude)
---

# Handoff — A1 verify ปิดจริง (ทดสอบสด mic) + เจอบั๊กจริง 5 ตัว

ต่อจาก [2026-07-03-live-plan-and-fish-audio-test.md](2026-07-03-live-plan-and-fish-audio-test.md) —
เซสชันนั้นทิ้งไว้ 3 decision ให้ CEO ตอบ, ข้อ 3 คือ "ปิด verify ค้าง (A1) ก่อนเริ่มรื้อ" CEO ตอบรับ
แล้วทดสอบจริงผ่านไมค์ต่อทันที (session ใหม่, `vault/history/2026-07-03_session-03.md`)
**เซสชันนี้ตัดจบก่อนเขียน handoff ทัน** — ไฟล์นี้เขียนย้อนหลังจากประวัติจริง + memory ที่บันทึกไว้แล้ว

## ทดสอบอะไร

CEO พูดผ่านไมค์จริงสั่งให้ Friday `dispatch_to_hermes` งานทดสอบง่ายๆ ("ตรวจสอบวันที่วันนี้แล้วตอบ")
ยืนยันคำสั่งด้วยเสียงจริง ("ยืนยันครับ") — ทดสอบ end-to-end ครั้งแรกของฟีเจอร์นี้ (โค้ดเขียนไว้ตั้งแต่
2026-07-02 แต่ยังไม่เคยทดสอบจริงผ่านไมค์)

## ผลลัพธ์: ทำงานถูกต้องทุกจุดที่ควบคุมได้ + เจอบั๊กจริง 5 ตัว

**`dispatch_to_hermes` core logic ไม่มีบั๊ก** — ส่ง task เข้า mailbox ถูก, Hermes claim ถูก, ตรวจจับ
`status=blocked/failed` ถูกต้อง, ไม่โกหกว่าสำเร็จ — **แต่ UX รอบการรายงานมีปัญหาจริง 2 จุด** (แก้ไข
จากที่เคยสรุปไว้ว่า "ไม่ค้างเงียบ" — ที่จริงเงียบจนต้องปลุก ดูข้อ 2):

1. **Hermes เอง crash จาก `pydantic_core` import error** ("cannot import name '__version__' from
   'pydantic_core'") — พังทั้ง kanban dispatcher (`t_ddcaf4cf.log`), บล็อกทุก task ที่เข้าคิว Hermes
   ตอนนี้ ไม่ใช่แค่ตัวทดสอบนี้ — **ต้องแก้ pydantic_core version ใน Hermes env ก่อน** ถึงจะ verify
   happy-path (Hermes ทำงานสำเร็จจริง) ได้จริง
2. **UX gap คู่กัน ใน `tool_dispatch_to_hermes`:** (ก) ระหว่างรอ Hermes รับงาน Friday เงียบไปด้วย
   ไม่มีเสียงคั่นระหว่าง blocking poll เลย (ข) ตอนที่ task โดนบล็อค **Friday ไม่รีบกลับมารายงานเอง**
   ต้องให้ CEO พูดปลุก (wake word ซ้ำ) ก่อนถึงจะกลับมารายงานผลได้ — ยังไม่ได้แก้
3. **STT ฟังผิด:** "ยืนยันครับ" บางครั้งถูกแปลงเป็น "ยันต์ครับ" — ตกหล่นจาก `CONFIRM_WORDS`/
   `_strip_confirm_particles` เดิม (พบจาก session-02 เช้าวันเดียวกัน)
4. **TV control ผิดซ้ำ 6 รอบติด:** สั่งเปิด YouTube บนทีวี ได้ "YouTube Kids" ผิดทุกครั้ง ทั้งที่
   ยืนยัน/แก้คำสั่งชัดเจนหลายรอบ ไม่เคยเปิดตัวปกติได้เลยในรอบนั้น — บั๊ก app-matching ฝั่ง TV control
5. **ค้นหาเว็บ (weather) auto-cancel เอง:** confirm แล้วเงียบเกิน timeout จน auto-cancel 2 รอบซ้อน
   โดยไม่รอคำตอบ CEO

Bug #3-5 **อยู่นอกขอบเขต Live-migration** (เป็นบั๊กในโค้ด walkie-talkie/TV-control ปัจจุบัน ไม่ใช่
เรื่อง Gemini Live) — พบแล้วแต่ยังไม่ได้แก้ ตาม [[feedback_dont_rush_next_step]] ไม่เร่ง CEO ตัดสินใจ
ว่าจะจัดการต่อยังไง

## สถานะ decision 3 ข้อ (จาก LIVE_UPGRADE_PLAN §7)

1. Gemini Live เป็นหลัก + walkie-talkie fallback? — **ยังไม่ตอบ**
2. ยอมรับสมองเปลี่ยนจาก gemma4 (Ollama) เป็น Gemini? — **ยังไม่ตอบ**
3. ปิด verify ค้างก่อนเริ่มรื้อ? — **ตอบรับแล้ว + ทดสอบจริงเสร็จแล้ว (เอกสารนี้)** — แต่เจอบั๊กใหม่
   ระหว่างทาง (ข้างบน) ยังไม่ได้แก้

## ถัดไป (สำหรับ session ใหม่)

1. รอ CEO ตอบ decision #1, #2 ที่เหลือ (ไม่เร่ง)
2. **Pivot กำลังเกิดขึ้น:** CEO กำลังออกแบบกับ Hermes โดยตรง (ไม่ผ่าน Commander) ให้เปลี่ยนจาก
   blocking-poll model เดิม เป็น **Friday สร้างงาน แล้วให้ n8n trigger แทน** — น่าจะแก้ทั้ง 2 UX gap
   ในข้อ 2 ข้างบนได้ Commander ไม่ต้องเข้าไปช่วยออกแบบเว้นแต่ถูกขอ
3. เต็มไมค์ทดสอบ voice pipeline อื่นๆ ที่ยังไม่เคยยืนยัน (ถ้า CEO อยากต่อ) ยังคงอ้างอิงตาม
   handoff เก่าหลายอันที่ทิ้งไว้

## ลงชื่อ

Commander (Claude) — session 2026-07-03 (เขียนย้อนหลัง)
