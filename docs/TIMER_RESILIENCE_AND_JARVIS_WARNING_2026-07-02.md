# set_timer ทนต่อการปิดโปรแกรม + เสียงเตือน "จาวิส" (2026-07-02)

**ทำโดย:** Commander (Claude)
**วันที่:** 2026-07-02
**โปรเจกต์:** `D:\AI-Workspace\projects\friday`
**ต่อจาก:** [LATENCY_PHASE1_2026-07-02.md](LATENCY_PHASE1_2026-07-02.md) — เซสชันเดียวกัน คนละแกนงาน (latency vs ความทนทาน/UX ของ timer)

---

## 1. 🎯 บริบท

ระหว่างคุยเรื่อง latency พี่ถามว่า "ตั้งเวลาไว้ 1 ชั่วโมงแล้วปิด Friday เลย จะยังมีเสียงเตือนไหม" — เช็คโค้ดแล้วพบว่า **ไม่รอด**: `set_timer` เดิมใช้ `threading.Thread(daemon=True)` ซึ่งตายไปพร้อม process ทันทีที่ปิดโปรแกรม ไม่มี warning ใดๆ เตือนความจำหายเงียบๆ

คุยกันแล้วตัดขอบเขต: **รอดจากการปิดโปรแกรม Friday (เครื่องยังเปิด) — ใช่ / รอดจากปิดเครื่องทั้งเครื่อง — ไม่ทำ** (เป็นไปไม่ได้ทางกายภาพที่จะให้เสียงออกลำโพงเครื่องที่ดับอยู่ ถ้าจะทำจริงต้องย้ายช่องทางเตือนไปทาง Hermes/OpenClaw → Telegram แทน ซึ่งเป็นคนละ scope)

---

## 2. ✅ set_timer — Task Scheduler เป็น backup

### ออกแบบ (hybrid ไม่ใช่แทนที่ทั้งหมด)

**เหตุผลที่ไม่ใช้ Task Scheduler อย่างเดียว:** ถ้า Friday ยังรันอยู่ตอนครบเวลา แล้วมีอีก process แยก (ที่ Task Scheduler เรียก) มาพูดพร้อมกัน จะชนกับ `AUDIO_LOCK`/`mic_listening` ที่ออกแบบไว้กันเสียงซ้อน/กันไมค์ได้ยินเสียงตัวเอง ของ process แยกไม่รู้จัก state ของ process หลักเลย

**เลยทำเป็น 2 ชั้น:**
1. **Primary — in-process daemon thread เดิม** ทำงานเหมือนเดิมทุกอย่าง (เร็ว, serialize กับเสียง/ไมค์ถูกต้อง)
2. **Backup — Windows Scheduled Task** ลงทะเบียนในพื้นหลังทันทีที่ thread เริ่ม (ไม่บล็อกการตอบกลับ) ผ่าน `_schedule_reminder_task()` ([friday_walkie_talkie.py:596](../src/friday_walkie_talkie.py#L596)) ตั้ง `StartWhenAvailable` ไว้ด้วย เผื่อพลาดเวลาไปตอนเครื่องปิด (ทดสอบด้วยว่ากรณีนี้ยังไม่ต้องกังวลไฟดับสั้นๆ — Task Scheduler ใช้เวลาสัมบูรณ์เทียบกับนาฬิกาเครื่อง (RTC มีแบตแยก) ไม่ใช่ตัวนับที่ต้อง "resume" อะไร)
3. Thread พูดสำเร็จ → เรียก `_cancel_reminder_task()` ([:622](../src/friday_walkie_talkie.py#L622)) ลบ backup ทิ้งทันที กันพูดซ้ำ 2 รอบ
4. Process ถูกปิดก่อนครบเวลา → thread ตายไปเฉยๆ (เหมือนเดิม) แต่ backup ที่ลงทะเบียนไว้แล้วยังอยู่ ยิงเองตามเวลาจริงผ่าน `fire_reminder.py` (ไฟล์ใหม่ ที่ [src/fire_reminder.py](../src/fire_reminder.py)) — สคริปต์ standalone ที่ decode ข้อความ (ส่งผ่าน base64 กัน encoding พัง) เรียก `speak()` เดิม แล้วลบ scheduled task ตัวเองทิ้ง

### จุดที่ตั้งใจไม่ทำ

- ไม่บล็อก `tool_set_timer()` รอผลลงทะเบียน Task Scheduler (ย้ายไปทำในพื้นหลังของ thread เอง) — ไม่งั้นทุกครั้งที่ตั้งเวลาจะช้าขึ้น 1-2 วิ ขัดกับงาน latency ที่เพิ่งทำไปก่อนหน้าในเซสชันเดียวกัน
- ลงทะเบียนไม่สำเร็จ (`_schedule_reminder_task` คืน `None`) → **ไม่ error ทิ้งงาน** แค่ไม่มี backup เฉยๆ ในเซสชัน — ไม่แย่ไปกว่าพฤติกรรมเดิมก่อนฟีเจอร์นี้

---

## 3. ✅ เสียงเตือน "จาวิส" (cloud ช้า)

**เดิม:** `ask_ollama()` พูด "ระบบ cloud มีปัญหา รอสักครู่นะคะนาย" (เสียงหญิงเดิม) ถ้ารอเกิน 25 วิ

**ใหม่:** เปลี่ยนเป็น **"ผมจาวิส รายงานครับ ไฟรเดย์กำลังเจอปัญหา รอสักครู่ครับนาย"** พูดด้วยเสียงผู้ชาย `th-TH-NiwatNeural` (ค่าคงที่ `JARVIS_VOICE`/`SLOW_WARNING_MESSAGE` ที่ [:30-31](../src/friday_walkie_talkie.py#L30))

**เพิ่ม `voice` parameter ให้ `speak()`/`generate_speech()`** ([:68](../src/friday_walkie_talkie.py#L68), [:152](../src/friday_walkie_talkie.py#L152)) — override เสียงได้เฉพาะครั้ง เสียงหลัก (Premwadee) จุดอื่นไม่กระทบ ใช้แค่ตอนพูดคำเตือนนี้จุดเดียว

**Cache ล่วงหน้าจริง:** เรียก `speak(SLOW_WARNING_MESSAGE, voice=JARVIS_VOICE)` จริงครั้งหนึ่งให้พี่ฟัง (ระบบ TTS cache จาก [LATENCY_PHASE1](LATENCY_PHASE1_2026-07-02.md) เก็บไฟล์เสียงลงดิสก์อัตโนมัติอยู่แล้ว ไม่ต้องสร้าง mechanism ใหม่) — ยืนยันด้วยการดัก `generate_speech` ว่าเรียก **0 ครั้ง** ในการพูดรอบถัดไป = cache hit จริง ไม่ต้องยิง edge-tts ซ้ำอีกเลยตั้งแต่นี้

---

## 4. 🧪 เทสที่เพิ่ม/แก้

| เทส | ตรวจอะไร |
|---|---|
| `schedule_reminder_task(live)` | ลงทะเบียน + ลบ Windows Scheduled Task จริงบนเครื่อง (ไม่ mock) |
| `set_timer(returns immediately)` | แก้เพิ่ม: stub `_schedule_reminder_task`/`_cancel_reminder_task` กัน unit test ไปแตะ Task Scheduler จริง + เช็คว่า thread เรียก cancel หลังพูดสำเร็จจริง |
| `ask_ollama(slow_warning)` | แก้ข้อความ/เสียงให้ตรงของใหม่ (`SLOW_WARNING_MESSAGE`, `JARVIS_VOICE`) |

**ยืนยันด้วยมือเพิ่ม (นอกชุดเทสอัตโนมัติ):**
1. รัน `tool_set_timer` จริงแบบ end-to-end (3 วิ) → เห็น scheduled task โผล่ระหว่างรอ → ยิงจริง → task หายอัตโนมัติหลังพูด
2. รัน `fire_reminder.py` ตรงๆ แบบเดียวกับที่ Task Scheduler จะเรียก → พูดจริง ไม่ error
3. เช็คไม่มี task ค้างบนเครื่องหลังทดสอบ
4. ดัก `generate_speech` call count ยืนยัน cache hit จริงของเสียงจาวิส

**ผลทดสอบ:** `test_tools.py` **51/51 passed**

---

## 5. ⚠️ ยังไม่ครอบคลุม

- **เคส "ปิด Friday จริงกลางคัน"** ไม่ได้ทดสอบตรงๆ (ต้อง kill process จริงระหว่างมีเวลาค้าง) — กลไกอาศัย Task Scheduler backup ที่ทดสอบแยกแล้วว่าทำงานถูกทุกจุดย่อย (ลงทะเบียนได้, ลบได้, `fire_reminder.py` รันได้จริง) แต่ end-to-end แบบปิดจริงยังเป็นความเชื่อมั่นทางทฤษฎี ไม่ใช่พิสูจน์แล้ว
- เคสปิดเครื่องทั้งเครื่อง — ตัดออกจาก scope ตามที่ตกลงกัน (ข้อ 1)

---

## 6. 🔗 อ้างอิง

- [LATENCY_PHASE1_2026-07-02.md](LATENCY_PHASE1_2026-07-02.md) — TTS cache ที่ฟีเจอร์เสียงจาวิสใช้ต่อ, loanword transliteration, pause_threshold
- [handoff/2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md](../handoff/2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md) — เซสชันก่อนหน้า
- [src/fire_reminder.py](../src/fire_reminder.py) — สคริปต์ standalone ที่ Task Scheduler เรียก
