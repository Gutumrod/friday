---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-03-live-plan-and-fish-audio-test.md
วันที่: 2026-07-03
ผู้เขียน: Commander (Claude)
---

# Handoff — Live upgrade plan (pending decision) + Fish Audio S2 Pro tested negative

ต่อจาก [2026-07-03-camera-vision-tools.md](2026-07-03-camera-vision-tools.md) และ
[2026-07-03-lg-tv-control-tools.md](2026-07-03-lg-tv-control-tools.md) — เซสชันเดียวกัน คนละแกนงาน
(เรื่องเสียงติ๊ง → คุยยาวไปถึงแผน Live upgrade → ทดสอบ local TTS ตัวใหม่)

## สรุปสิ่งที่เกิดขึ้น (ลำดับเวลา)

1. คุยเรื่องเสียง "ติ๊ง" บอกสถานะไมค์ (ยังไม่ได้ทำ — แค่คุยแนวคิด ไม่ได้ implement)
2. ต่อยอดไปถึงคำถามใหญ่: ถ้าทำ Friday แบบ full-duplex เหมือน Gemini Live ในอนาคต ต้องรื้อโค้ด
   แค่ไหน — เขียน [docs/LIVE_MIGRATION_READINESS_2026-07-03.md](../docs/LIVE_MIGRATION_READINESS_2026-07-03.md)
   ไล่ทุกฟังก์ชันแยกเป็น ✅ รอด / 🔧 รอดแต่ต้องมี adapter / 🔴 รื้อทั้งหมด
3. **พบว่ามี session คู่ขนานอื่น** (จำลอง "Fable 5" — CEO ยืนยันว่าเป็นร่างโมเดลเดียวกัน ไม่ใช่คนละคน)
   วิจัยเรื่องนี้ไปไกลกว่าแล้ว เขียนไว้ที่ [docs/LIVE_UPGRADE_PLAN_2026-07-03.md](../docs/LIVE_UPGRADE_PLAN_2026-07-03.md)
   (สรุปแนะนำ Gemini Live API เป็นหลัก + walkie-talkie เดิมเป็น fallback, แผน 4 เฟส A/B/C/D)
   — ไฟล์นี้นอนอยู่แบบ **untracked ใน git** ตอนเจอ เก็บ commit ให้แล้ว
4. เปิดอ่านเอกสารนั้นด้วยกันกับ CEO แบบ interactive (render เป็น widget ในแชทด้วย)
5. CEO ติดเรื่องงบ (option Gemini Live paid tier $20-45/เดือนถ้าเกิน free quota) — สรุปว่า **Phase A
   (ปิดงานค้าง + แยกโค้ด) ไม่เสียตังค์เลย ไม่ต้องรอตัดสินใจเรื่องงบก่อนเริ่ม Phase A**
6. CEO เล่าว่าเคยเห็นโพสต์อ้างว่ามี local Thai voice model เสียงชัดมาก + ดูกล้อง + คุม 3D map ได้
   วิเคราะห์ร่วมกันว่าน่าจะเป็น Gemini Live/Project Astra demo จริง แต่คำว่า "local" น่าสงสัย
   (อาจเป็นแค่ script รัน local แต่ยังยิง cloud API อยู่ดี)
7. **ไล่หา local Thai TTS ตัวใหม่จริงจัง** (ตอบคำถามที่ CEO ไม่อยากทิ้ง) — เจอ **Fish Audio S2 Pro**
   (ปล่อยมี.ค. 2026, มาทีหลังงานวิจัยเดิมของ Fable) เปิด weight จริง self-host ได้ฟรี (non-commercial)
   และ **ยืนยันแล้วว่ารองรับภาษาไทยในลิสต์**

## ทดสอบ Fish Audio S2 Pro จริง — ผลลบ

**พยายาม self-host ในเครื่องนี้ (WSL2 Ubuntu, RTX 2080 Ti 11GB VRAM):**
- ติดตั้งสำเร็จ (clone repo, venv, `pip install -e '.[cu129]'`, torch 2.8.0) — ไม่มีปัญหา
- ดาวน์โหลด checkpoint สำเร็จ (11GB, จาก HuggingFace `fishaudio/s2-pro`)
- **รัน inference จริงแล้ว VRAM ไม่พอ** — doc ทางการบอกชัดว่า "แนะนำ GPU อย่างน้อย 24GB" (ขั้นต่ำ 12GB)
  เครื่องนี้มีแค่ 11GB รวม ผลคือ **CUDA OOM รุนแรงจน WSL GPU passthrough ค้างทั้งระบบ** ต้อง
  `wsl --terminate Ubuntu` แล้วเริ่มใหม่ ไฟล์ log หายหมดเพราะ `/tmp` เป็น tmpfs
- **ล้างทิ้งหมดแล้วตามที่ CEO สั่ง** — ลบ `~/fish-speech` (รวม checkpoint 11GB) + `wsl --shutdown`
  คืนพื้นที่เต็ม ไม่มีอะไรค้างในเครื่องจากการทดสอบนี้

**ทดสอบผ่าน HuggingFace Space แทน** (ไม่ต้อง self-host, ไม่ต้องสมัครสมาชิก):
https://huggingface.co/spaces/artificialguybr/fish-s2-pro-zero
CEO ลองพิมพ์ข้อความไทยจริงด้วยตัวเอง — **ผลลัพธ์: "ไม่ต่างจากที่เคยลองมาเลย"** (เทียบกับ
VachanaTTS ที่เคยสรุปไปแล้วว่า "เหมือนชาวเขาลงมา" ไม่ผ่านมาตรฐาน)

### สรุปข้อสรุปเรื่อง local Thai TTS (อัปเดตจาก LIVE_UPGRADE_PLAN)

**Fish Audio S2 Pro ไม่ใช่คำตอบ** — แม้เปิด weight จริง รองรับไทยในลิสต์ แต่คุณภาพเสียงไทยจริง
**ไม่ผ่านมาตรฐานเดียวกับ VachanaTTS** (CEO ฟังเองยืนยัน) ตอกย้ำข้อสรุปเดิมของ
[LIVE_UPGRADE_PLAN](../docs/LIVE_UPGRADE_PLAN_2026-07-03.md) ข้อ 2 ว่า **local Thai TTS ยังไม่พร้อมจริง
(4/10)** — ไม่ใช่แค่ VachanaTTS ตัวเดียวที่แย่ ลองโมเดลใหม่กว่าก็ยังแย่เหมือนกัน เพิ่มน้ำหนักให้
ข้อเสนอ **Gemini Live เป็นเส้นทางหลัก** ในเอกสารนั้นแข็งแรงขึ้น (ไม่ใช่แค่ไม่มีตัวเลือก local ที่ดี
กว่า — ลองจริงแล้วซ้ำสองรอบว่าแย่จริง)

## สถานะที่ค้างอยู่ตอนนี้

**3 decision ที่ CEO ยังไม่ได้ตอบ** (จาก [LIVE_UPGRADE_PLAN §7](../docs/LIVE_UPGRADE_PLAN_2026-07-03.md#7-❓-decision-ที่-ceo-ต้องเคาะก่อนเริ่ม)):
1. เห็นชอบ Gemini Live เป็นหลัก + walkie-talkie เป็น fallback ไหม?
2. ยอมรับว่า "สมอง" เปลี่ยนจาก `gemma4:31b-cloud` เป็น Gemini ไหม?
3. ปิด verify ค้าง (A1) ก่อนเริ่มรื้อ ตามที่แนะนำไหม?

**งบเป็นข้อกังวลที่ยังไม่คลี่คลาย** — แต่ไม่บล็อก Phase A (ฟรี) เริ่มได้เลยถ้า CEO พร้อม โดยไม่ต้อง
รอตัดสินใจเรื่อง Gemini paid tier ก่อน

**เครื่องมือ/ไฟล์ที่เพิ่มวันนี้ ยังไม่เกี่ยวกับการรื้อ Live** — กล้อง+ทีวี (ดู handoff อีก 2 ไฟล์)
เป็นงานที่อยู่ในกลุ่ม ✅ "รอด" ตาม LIVE_MIGRATION_READINESS อยู่แล้ว ไม่กระทบแผน Live

## ถัดไป (สำหรับ session ใหม่)

1. รอ CEO ตอบ 3 decision ข้างต้น ก่อนเริ่ม Phase A จริงจัง
2. ถ้าอยากปิดงานค้างที่ Phase A1 พูดถึงไว้ก่อน — verify full voice pipeline ผ่านไมค์จริง +
   `dispatch_to_hermes` end-to-end จริง (ยังไม่เคยทำ ตามที่ handoff เก่าหลายอันย้ำไว้)
3. ไม่ต้องกลับไปลอง local Thai TTS ตัวอื่นอีกโดยไม่มีเหตุผลใหม่ — ทดสอบจริงแล้ว 2 ตัว
   (VachanaTTS, Fish Audio S2 Pro) ทั้งคู่ไม่ผ่าน ข้อสรุป "local ยังไม่พร้อม" มีน้ำหนักพอแล้ว

## ลงชื่อ

Commander (Claude) — session 2026-07-03
