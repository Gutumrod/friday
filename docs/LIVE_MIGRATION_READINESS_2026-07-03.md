# Live (full-duplex) migration readiness — อะไรรอด อะไรต้องรื้อ (2026-07-03)

**ทำโดย:** Commander (Claude)
**วันที่:** 2026-07-03
**โปรเจกต์:** `D:\AI-Workspace\projects\friday`
**ต่อจาก:** [CAMERA_AND_TV_CONTROL_2026-07-03.md](CAMERA_AND_TV_CONTROL_2026-07-03.md) — เซสชันเดียวกัน

---

## 1. 🎯 บริบท

คุยกันเรื่องเสียง "ติ๊ง" บอกสถานะไมค์ แล้วต่อไปถึงคำถามใหญ่กว่า: ถ้าวันหน้าจะทำ Friday
แบบ **full-duplex ต่อเนื่องเหมือน Gemini Live** (ไม่มีรอบ ฟัง→คิด→ตอบ แยกกันชัดเจนแบบตอนนี้)
จะต้องรื้อโค้ดปัจจุบันแค่ไหน — เอกสารนี้ไล่ทุกฟังก์ชันในโค้ดปัจจุบัน แยกว่า **รอดได้ตรงๆ /
รอดแต่ต้องมี adapter / ต้องรื้อทั้งหมด** จะได้ไม่ต้องมานั่งไล่ทีหลังตอนใกล้ทำจริง

**นิยาม 3 กลุ่ม:**
- ✅ **รอด (Capability layer)** — ตรรกะทำงานจริงของแต่ละ tool ไม่เกี่ยวกับว่าเสียง/ข้อความเข้ามายังไง
- 🔧 **รอดแต่ต้องมี adapter** — concept ยังใช้ได้ แต่ interface/format ต้องปรับให้เข้ากับ API ใหม่
- 🔴 **รื้อทั้งหมด** — ผูกติดกับสถาปัตยกรรม turn-based + text-in/text-out ของ Ollama โดยตรง

---

## 2. ✅ รอด — Capability layer (tool_* ทั้งหมด + ตัวช่วยของมัน)

ตรรกะ "ทำอะไรจริง" ของทุก tool ไม่แคร์ว่าถูกเรียกจากคำสั่งเสียงแบบ turn-based หรือ
audio stream ต่อเนื่อง — **กลุ่มนี้คือของที่ทำวันนี้เกือบทั้งหมด ไม่เสียเปล่า:**

| กลุ่ม | ฟังก์ชัน |
|---|---|
| ระบบ/แอป | `tool_get_time`, `tool_disk_space`, `tool_open_app`, `tool_close_app`, `tool_set_volume`, `tool_list_processes`, `tool_open_web`, `tool_system_status`, `tool_network_status`, `tool_empty_recycle_bin` |
| Clipboard/สื่อ | `tool_clipboard_read`, `tool_clipboard_write`, `tool_media_control` |
| ความจำ/ค้นหา | `tool_remember`, `tool_search_web` (+ `_looks_explicit`, `_strip_injection_tags`), `load_facts`, `migrate_legacy_day_files`, `start_new_session`, `log_to_vault` |
| Timer/Alarm | `tool_set_timer`, `tool_set_alarm`, `tool_list_timers`, `tool_cancel_timer` (+ `_register_timer`, `_schedule_reminder_task`, `_cancel_reminder_task`, `_reminder_python`) และ **`fire_reminder.py` ทั้งไฟล์** |
| Hermes | `tool_dispatch_to_hermes` |
| กล้อง (วันนี้) | `tool_open_camera`, `tool_close_camera`, `tool_look_camera`, `_ask_ollama_vision` (ดู 4.3) |
| ทีวี (วันนี้) | `tool_tv_power`, `tool_tv_volume`, `tool_tv_launch_app`, `tool_tv_play_video`, `tool_tv_remote_button`, `_tv_connect` |

**สรุป:** ฟีเจอร์กล้อง+ทีวีที่เพิ่งทำวันนี้ทั้งหมดอยู่ในกลุ่มนี้ — วันหน้าทำ Live แค่เปลี่ยนวิธี
"เรียก" ฟังก์ชันพวกนี้ ตัวฟังก์ชันเองไม่ต้องแตะเลย

---

## 3. 🔴 รื้อทั้งหมด — Orchestration/IO layer (ผูกกับ turn-based text pipeline)

| ฟังก์ชัน | ทำไมรื้อ |
|---|---|
| `listen_mic` ([:315](../src/friday_walkie_talkie.py#L315)) | STT แบบ "อัดจบประโยคแล้วแปลงทีเดียว" (`recognize_google`) — full-duplex ต้องส่งเสียงสตรีมเข้าโมเดลต่อเนื่อง ไม่มี "จบประโยค" ให้รอ |
| `speak`, `generate_speech_fallback`, `remove_emojis`, `_transliterate_loanwords` ([:165,140,80,110](../src/friday_walkie_talkie.py#L165)) | TTS แยก (edge-tts) แปลงข้อความ→เสียง — โมเดล audio-native พูดออกมาเป็นเสียงตรงๆ ไม่ต้องมีขั้นนี้เลย |
| `ask_ollama` ([:356](../src/friday_walkie_talkie.py#L356)) | เรียก Ollama text chat API ตรงๆ — โมเดลเสียงแบบ Live ใช้ API/protocol คนละแบบ (WebSocket streaming ไม่ใช่ request/response) |
| `CONFIRM_GATED`, `find_first_gated_tool_call`, `_should_announce_cancel`, `_strip_confirm_particles`, `CONFIRM_WORDS`, `_execute_search_web` ([:1266,1369,1380,1228](../src/friday_walkie_talkie.py#L1266)) | ทั้งกลไกอาศัย "รอบที่แน่นอน" รอคำตอบยืนยันตรงคำ — ไม่มี "รอบ" แบบนี้ในสตรีมต่อเนื่อง ต้องคิดกลไกยืนยันใหม่ทั้งหมด (เช่น interrupt-based) |
| `build_system_prompt` ([:1405](../src/friday_walkie_talkie.py#L1405)) | เนื้อหาส่วนใหญ่ (persona, กติกา) น่าจะย้ายไปใช้ได้ แต่ format/การฉีดเข้าโมเดลเปลี่ยนไปตาม API ใหม่ |
| `main` ([:1440](../src/friday_walkie_talkie.py#L1440)) | ทั้ง loop คือ sequential/blocking (ฟังจบ→คิด→พูด→วนใหม่) ต้องเขียนใหม่เป็น async event loop รับส่งพร้อมกันได้ รองรับ user แทรกกลางคัน |

---

## 4. 🔧 รอดแต่ต้องมี adapter (concept ใช้ได้ format ต้องปรับ)

### 4.1 `TOOLS` / `TOOL_SCHEMAS` ([:1053,1086](../src/friday_walkie_talkie.py#L1053))
ตัว dict ที่ map ชื่อ→ฟังก์ชัน (`TOOLS`) รอดตรงๆ ไม่ต้องแตะ — แต่ `TOOL_SCHEMAS` (JSON schema
แบบ Ollama native tool-calling) ต้องแปลงรูปแบบให้ตรงกับ function-calling spec ของ API ใหม่
(เช่น Gemini Live มี function calling ของตัวเอง คนละ schema format) เนื้อหา
name/description/parameters ส่วนใหญ่ก็อปวางแล้วปรับ format พอ ไม่ต้องคิดใหม่

### 4.2 `_pack_args`, `_TOOL_ARG_KEY`, `run_native_tools` ([:1211,931,1390](../src/friday_walkie_talkie.py#L1211))
Glue code สำหรับแปลง args ที่โมเดลส่งมา (JSON) เป็น string เดี่ยวที่ tool_* เดิมรับ (ทำไว้ตอน
migrate จาก text-tag เป็น native tool-calling) — ยังต้องมี glue layer แบบนี้อยู่ดีไม่ว่า
backend จะเป็นอะไร แค่ปรับให้ตรงกับ arguments format ของ API ใหม่

### 4.3 `_ask_ollama_vision` ([:868](../src/friday_walkie_talkie.py#L868))
วันนี้ยิงภาพเข้า `gemma4:31b-cloud` แยกเป็น request เดี่ยว — โมเดล Live ส่วนใหญ่ (เช่น
Gemini Live) รับวิดีโอ/ภาพเป็น input stream ได้ตรงๆ อยู่แล้วในตัว อาจไม่ต้องมีฟังก์ชันนี้แยก
เลยด้วยซ้ำ (กล้องอาจกลายเป็นแค่ video stream เข้าโมเดลเดียวกับเสียง ไม่ใช่ tool call แยก) —
**ต้องตัดสินใจตอนเลือก API จริง ไม่ใช่ตอนนี้**

---

## 5. ⚠️ ยังไม่ครอบคลุม

- ยังไม่ได้เลือก API/โมเดลเป้าหมายสำหรับ Live จริง (Gemini Live เป็นแค่ตัวอย่างอ้างอิง ไม่ใช่
  การตัดสินใจ) — การแบ่งกลุ่มนี้อิงจากสถาปัตยกรรม full-duplex ทั่วไป ไม่ใช่ API เจาะจงตัวใดตัวหนึ่ง
  รายละเอียด adapter จริงจะขึ้นกับ API ที่เลือกใช้
- ไม่ได้ประเมินต้นทุน/เวลาที่ต้องใช้ทำ Live จริง เอกสารนี้บอกแค่ "อะไรรอด" ไม่ใช่ "แผนงาน"

---

## 6. 🔗 อ้างอิง

- [CAMERA_AND_TV_CONTROL_2026-07-03.md](CAMERA_AND_TV_CONTROL_2026-07-03.md) — ฟีเจอร์กล้อง/ทีวีที่อยู่ในกลุ่ม ✅ รอด
- [handoff/2026-07-02-dispatch-to-hermes-implemented.md](../handoff/2026-07-02-dispatch-to-hermes-implemented.md) — บริบท native tool-calling migration ที่ `_pack_args`/`_TOOL_ARG_KEY` มาจาก
