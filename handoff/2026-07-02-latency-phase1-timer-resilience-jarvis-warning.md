---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-02-latency-phase1-timer-resilience-jarvis-warning.md
วันที่: 2026-07-02
ผู้เขียน: Commander (Claude)
---

# Handoff — Latency Phase 1 (TTS Cache/Loanword/pause_threshold), set_timer ทนต่อการปิดโปรแกรม, เสียงเตือน "จาวิส"

ต่อจาก [2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md](2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md) — เซสชันใหม่ วันเดียวกัน อ่านไฟล์นั้นก่อนถ้ายังไม่เห็น (native tool-calling, tiered confirm-gate, บั๊ก CONFIRM_WORDS เพิ่งแก้ตอนนั้น)

## สรุปสิ่งที่ทำในเซสชันนี้ (เรียงลำดับ)

### 0. เก็บงานค้างจาก handoff ก่อนหน้า
Revert `TESTING_LOCAL_VOICE_ONLY = False` ([friday_walkie_talkie.py:29](../src/friday_walkie_talkie.py#L29) ตอนนั้น — เลขบรรทัดขยับไปแล้วหลังงานเซสชันนี้) รัน `test_tools.py` ยืนยัน 48/48 ผ่านหลัง revert (baseline ก่อนเริ่มงานใหม่)

### 1. วิเคราะห์ latency ของ pipeline การพูดคุย
CEO สังเกตดีเลย์ช่วง "พูดเสร็จ → พูดตอบ → กว่าจะขึ้นกำลังแปลงคำพูด" วิเคราะห์ร่วมกันแล้วพบ **3 network call ต่อกันเป็นคิว ไม่มี overlap**: STT (Google) → Ollama cloud (`stream: False` = รอจนโมเดลคิดจบ 100% ก่อนได้อะไรกลับมาเลย) → edge-tts นอกจากนี้ยังเจอ `r.pause_threshold = 1.5` (รอเงียบ 1.5 วิ ก่อนตัดจบประโยค) เป็นดีเลย์แยกอีกจุด

ตัดสินใจ: **ยังไม่ทำ streaming** (เสี่ยงกระทบ `CONFIRM_GATED` ถ้า parse `tool_calls` แบบ incremental ผิด ต้องวางแผนแยกก่อน) เลือกทำ Phase 1-2 (cache, loanword fix, pause_threshold) ก่อน เพราะไว เสี่ยงต่ำ ไม่แตะ turn-taking/safety-gate

### 2. Phase 1 — TTS Cache + Loanword Transliteration + pause_threshold
รายละเอียดเต็มดู [docs/LATENCY_PHASE1_2026-07-02.md](../docs/LATENCY_PHASE1_2026-07-02.md) สรุปสั้น:
- **TTS cache ทั่วไป** (`TTS_CACHE_DIR`) — memoize เสียงด้วย hash(voice+text) เก็บลงดิสก์ถาวร ประโยคซ้ำ (เช่น คำถาม/cancel ของ gated tools) ครั้งที่ 2 ขึ้นไปข้าม TTS call
- **`_transliterate_loanwords()`** — เรียก gemma สะกดคำอังกฤษเป็นไทยก่อนเข้า fallback TTS (VachanaTTS) แก้ปัญหา "notepad" ออกเสียงเพี้ยน ตั้งใจไม่ reuse `ask_ollama()` (เสี่ยง deadlock กับ `AUDIO_LOCK` ที่ไม่ reentrant) เขียน request แยกเอง
- **`pause_threshold` 1.5 → 0.8s**
- เจอ+แก้บั๊ก test-pollution: เทสที่เรียก `speak()` จริงต้อง isolate `TTS_CACHE_DIR` ไม่งั้นรันซ้ำจะพังเพราะไปเจอ cache จริงจาก run ก่อนหน้า
- **ทดสอบ:** 50/50 passed (รันซ้ำ 2 รอบยืนยันไม่มี pollution)

### 3. ทดสอบ open_app/close_app จริง (นอกชุด automated test)
เรียก `tool_open_app("notepad")`/`tool_close_app("notepad")` ตรงๆ เช็คด้วย `psutil` ยืนยัน process จริงเปิด-ปิดตามคำสั่ง ไม่ค้าง — เป็นการยืนยัน tool function เอง ไม่ใช่ full voice pipeline (ไม่มีไมค์ให้ทดสอบ STT/confirm-gate จริง)

### 4. set_timer ทนต่อการปิดโปรแกรม Friday
CEO ถามว่าตั้งเวลาไว้แล้วปิด Friday จะยังเตือนไหม — เช็คโค้ดพบว่า **ไม่รอด** (`threading.Thread(daemon=True)` ตายไปกับ process ทันที ไม่มี warning) คุยกันตัดขอบเขต: รอดจากปิดโปรแกรม (เครื่องยังเปิด) เท่านั้น — ปิดเครื่องทั้งเครื่องเป็นไปไม่ได้ทางกายภาพ ถ้าจะทำจริงต้องย้ายไปทาง Hermes/OpenClaw → Telegram (คนละ scope)

รายละเอียดเต็มดู [docs/TIMER_RESILIENCE_AND_JARVIS_WARNING_2026-07-02.md](../docs/TIMER_RESILIENCE_AND_JARVIS_WARNING_2026-07-02.md) สรุปสั้น:
- **Hybrid ไม่ใช่แทนที่ทั้งหมด:** in-process thread ยังเป็น primary (serialize กับเสียง/ไมค์ถูกต้องผ่าน `AUDIO_LOCK`/`mic_listening`) + **Windows Scheduled Task เป็น backup** ลงทะเบียนในพื้นหลัง (ไม่บล็อกการตอบกลับ) ผ่าน `_schedule_reminder_task()` ตั้ง `StartWhenAvailable` กันพลาดเวลาตอนเครื่องปิด
- Thread พูดสำเร็จ → เรียก `_cancel_reminder_task()` ลบ backup กันพูดซ้ำ
- **ไฟล์ใหม่:** `src/fire_reminder.py` — standalone script ที่ Task Scheduler เรียกตอน process หลักตายไปแล้ว (decode ข้อความ base64, เรียก `speak()` เดิม, ลบ task ตัวเองทิ้ง)
- **ทดสอบ:** เพิ่ม live test จริงบน Task Scheduler + ยืนยันมือ (end-to-end 3 วิ, เรียก `fire_reminder.py` ตรงๆ, เช็คไม่มี task ค้าง) **51/51 passed**
- **ยังไม่ทดสอบ:** เคส "ปิด Friday จริงกลางคัน" (ต้อง kill process จริงระหว่างมีเวลาค้าง) — ทดสอบแยกทุกจุดย่อยแล้วว่าทำงานถูก แต่ end-to-end จริงยังเป็นความเชื่อมั่นทางทฤษฎี

### 5. เสียงเตือน "จาวิส" (cloud ช้า)
เปลี่ยนข้อความเตือนตอน Ollama cloud ช้า (>25 วิ) จาก "ระบบ cloud มีปัญหา รอสักครู่นะคะนาย" (เสียงหญิงเดิม) เป็น **"ผมจาวิส รายงานครับ ไฟรเดย์กำลังเจอปัญหา รอสักครู่ครับนาย"** เสียงผู้ชาย (`th-TH-NiwatNeural`)

- เพิ่ม `voice` parameter ให้ `speak()`/`generate_speech()` override เสียงเฉพาะครั้ง (เสียงหลัก Premwadee จุดอื่นไม่กระทบ)
- **Cache ล่วงหน้าจริง** — เรียก `speak()` ครั้งจริงให้ CEO ฟัง ระบบ cache จาก Phase 1 เก็บลงดิสก์อัตโนมัติ ยืนยันด้วยการดัก `generate_speech` call count = 0 ครั้งในการพูดรอบถัดไป (cache hit จริง)
- **ทดสอบ:** อัปเดตเทส `ask_ollama(slow_warning)` ให้ตรงข้อความ/เสียงใหม่ **51/51 passed**

## ทดสอบ

**51/51 ทั้งหมด** (`test_tools.py` ผ่าน conda env `friday` — ดู [WALKTHROUGH.md](../docs/WALKTHROUGH.md)) รันซ้ำหลายรอบระหว่างเซสชันยืนยันไม่มี flakiness/pollution

## ⚠️ สิ่งที่ต้องทำก่อนใช้งานจริงต่อ (ยังไม่ได้ทำ)

1. **CEO ทดสอบพูดจริงผ่าน full voice pipeline** — "เปิด Notepad" ด้วยเสียงจริง (mic→STT→LLM→confirm-gate→execute) ยืนยันบั๊ก CONFIRM_WORDS ที่แก้ไปเซสชันก่อนหน้ายังทำงานถูก + สังเกต latency ที่ควรไวขึ้นจาก Phase 1/2 นี้ในตัว — ผมทดสอบได้แค่ tool function ตรงๆ เพราะไม่มีไมค์
2. **ทดสอบ "ปิด Friday จริงกลางคัน" ระหว่างมีเวลาค้าง** ยืนยัน Task Scheduler backup ยิงจริง end-to-end (ตอนนี้ทดสอบแยกทุกจุดย่อยแล้ว แต่ยังไม่เคย kill process จริงทดสอบทั้งสาย)

## ค้างจากก่อนหน้า (ยังไม่เปลี่ยนสถานะ)

- ตอบ Hermes เรื่อง contract 3 ข้อสำหรับ `dispatch_to_hermes` — รอ CEO ยืนยันเนื้อหา
- Test 2 (set_timer stress escalation) — รอ CEO ยืนยัน ceiling
- Wake word / voiceprint แท้ๆ — พักไว้ (ถ้า CEO เปลี่ยนใจอยากได้ speaker auth จริงในอนาคต)
- **Phase 3 (streaming Ollama response + sentence-chunked TTS)** — ยังไม่เริ่ม เสี่ยงกระทบ `CONFIRM_GATED` ถ้า parse `tool_calls` แบบ incremental ผิด ต้องวางแผนแยกก่อนลงมือ (ตัวที่หนักสุดในโครง latency เดิม แต่ก็เสี่ยงสุด)
- **Phase 4 (VAD/interruptible barge-in, local model แทน cloud, wake word)** — พักไว้ตามการตัดสินใจเดิม
- **Reminder ที่รอดจากปิดเครื่องทั้งเครื่อง** — ต้องรอ Friday เชื่อมกับทีม Hermes/OpenClaw (mailbox dispatch) ก่อนถึงจะย้ายช่องทางเตือนไปทาง Telegram ได้จริง — คนละ scope จาก set_timer ที่ทำวันนี้
- Telegram integration — ยังไม่เริ่ม

## ลงชื่อ

Commander (Claude) — session 2026-07-02
