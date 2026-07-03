---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-03-camera-vision-tools.md
วันที่: 2026-07-03
ผู้เขียน: Commander (Claude)
---

# Handoff — open_camera / look_camera / close_camera

## สรุป

CEO ถามว่าต่อกล้องเว็บแคมให้ Friday ดูภาพได้ไหม ชี้แจงว่าไม่ต้องการแบบ Gemini Live
(สตรีมต่อเนื่อง) — ต้องการ 2 trigger แยกกัน: สั่งเปิดกล้อง แล้วค่อยถามว่าเห็นอะไรทีหลัง
ไม่ต้อง poll ต่อเนื่อง (ประหยัด API call)

## สิ่งที่ทำ

- **`tool_open_camera()`** — เปิด `cv2.VideoCapture(0)` เก็บ handle ไว้ใน `_camera` global
  **CONFIRM_GATED** (จุดเดียวที่ถามยืนยัน — เหตุผลเดียวกับ clipboard_read: เปิดกล้องเองโดยไม่ตั้งใจ
  จากเสียงที่ฟังผิดเป็นความเสี่ยง privacy)
- **`tool_look_camera(question)`** — ถ่าย 1 เฟรมจากกล้องที่เปิดอยู่ ส่งเข้า `gemma4:31b-cloud`
  (ยืนยันแล้วว่ารับภาพได้) ผ่าน `_ask_ollama_vision()` ใหม่ (เรียก Ollama ตรง ไม่ผ่าน
  `ask_ollama()` เพราะไม่มี history/tools) **ไม่เปิดกล้องเอง** — ถ้าเรียกก่อน open_camera จะ error
  สุภาพ ไม่ใช่เปิดกล้องแทน
- **`tool_close_camera()`** — release device คืน
- ทั้ง 3 ตัวใหม่ **ungated ยกเว้น open_camera** — ตามที่ CEO ต้องการ ไม่ให้ถามซ้ำทุกครั้งที่ถามว่า
  "เห็นอะไร" หลังเปิดกล้องแล้ว
- เพิ่ม `opencv-python` ใน `requirements.txt` **และติดตั้งจริงใน conda env `friday`** แล้ว (เดิมไม่มี
  จะพังตอน import ถ้าไม่ติดตั้งก่อน)

## ทดสอบ

**58/58 passed** (56 เดิม + 2 ใหม่): gate wiring ถูกต้อง, roundtrip open→look→close ครบ
(mock `cv2.VideoCapture`/`requests.post`) รวม guard rail: look ก่อน open ต้อง refuse,
open ซ้ำต้องเป็น no-op, close ซ้ำต้อง idempotent

**Live-verified จริงกับกล้องเครื่องนี้** — เปิดกล้องจริง, โมเดลอธิบายภาพห้องออกมาถูกต้อง
(เห็นเก้าอี้ขาว พัดลม ตะกร้า), ปิดกล้องคืน resource สำเร็จ

## ค้างจากก่อนหน้า (ไม่เปลี่ยนสถานะ)

เหมือน handoff ก่อนหน้าทั้งหมด — ยังไม่มีอะไรเปลี่ยนสถานะจากตัวนี้

## ลงชื่อ

Commander (Claude) — session 2026-07-03
