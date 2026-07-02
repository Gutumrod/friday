---
path: D:\AI-Workspace\projects\jarvis\handoff\2026-07-01-tools-hardening-p2-and-session-files.md
วันที่: 2026-07-01
ผู้เขียน: Commander (Claude)
---

# Handoff — Friday: 7 Tool ใหม่ + Bug Fix 4 ข้อ + Session-File Redesign

ต่อจาก [2026-07-01-toolset-hardening-and-roadmap.md](file:///D:/AI-Workspace/projects/jarvis/handoff/2026-07-01-toolset-hardening-and-roadmap.md) เซสชันเดียวกัน คนละช่วง (CEO ออกไปนอกบ้านแล้วกลับมา) — อ่านไฟล์นั้นก่อนถ้ายังไม่เห็น (9 tool เดิม, confirm-flow ของ close_app, roadmap 4 phase)

## สรุปสิ่งที่ทำในช่วงนี้

### 1. เทส hardening ของเดิม (9 tool) — ผ่านหมด เจอปัญหา environment แต่หาเจอแล้ว
รันเทส `test_tools.py` เดิมครั้งแรกแล้วพบว่า Python ที่เช็ค 4 ตัว (`C:\Python314`, WindowsApps store python, Miniconda base env, py launcher 3.11) **ไม่มีตัวไหนติดตั้ง `pygame`/`speech_recognition`/`ddgs` ครบ** (`pygame` ไม่มี wheel สำหรับ Python 3.14 ด้วย) ทำให้ต้อง stub `pygame`/`speech_recognition` ชั่วคราวเพื่อรันเทสได้ก่อน (ไม่แตะ audio/mic จริง)

**✅ หาเจอแล้วในช่วงท้าย session:** env ที่ CEO ใช้รันอยู่ก่อนคือ `C:\Users\Win10\miniconda3\envs\subtitle-aligner\python.exe` (Python 3.10.20) — มี `pygame 2.6.1`, `SpeechRecognition 3.17.0`, `PyAudio 0.2.14`, `ddgs 9.14.4`, `edge-tts 7.2.8` ครบตาม `requirements.txt` เป๊ะ (memory เก่าของ Claude เคยจดชื่อ env นี้ไว้แล้วจริงๆ แค่ตอนไล่หาตอนแรกลืมเช็คตัวนี้ ไปเช็ค base env เปล่าผิดตัว) รัน `test_tools.py` ซ้ำด้วย python ตัวนี้ (ไม่ stub อะไรเลย) ผ่าน 29/29 เหมือนกัน — ยืนยันว่าไม่มีปัญหา import จริง

**อัปเดตท้าย session:** CEO ถามว่า `subtitle-aligner` เป็น env ที่เอาไว้ตัดซับวิดีโอ ใช้ร่วมกับ Friday จะรบกวนกันไหม — ตอบว่าไม่รบกวนกัน (คนละโปรเซสกันตอนรัน) แต่มีความเสี่ยงระยะยาวเรื่อง dependency ชนกันตอน pip install ของใหม่ CEO เลยให้**แยก env ใหม่ชื่อ `friday` ออกมาเลย** (Python 3.10 ให้ตรงกับตัวที่พิสูจน์แล้วว่าใช้ได้) ติดตั้ง `requirements.txt` + `psutil` (เจอว่า `psutil` ถูกใช้จริงในโค้ดแต่ไม่ได้อยู่ใน requirements.txt — เพิ่มตอนติดตั้งด้วยเลย ควรใส่ลงไฟล์ requirements.txt ในโค้ดจริงด้วย ยังไม่ได้แก้) รัน `test_tools.py` ซ้ำกับ env ใหม่ **29/29 PASS** เหมือนกัน

**คำสั่งรันปัจจุบัน (env ล่าสุด, ใช้ตัวนี้):**
```
C:\Users\Win10\miniconda3\envs\friday\python.exe friday_walkie_talkie.py
```
(อัปเดต `WALKTHROUGH.md` ให้ตรงแล้ว — `subtitle-aligner` เก็บไว้ทำงานตัดซับต่อไปตามเดิม ไม่ต้องยุ่งกับมันอีก)

### 2. เพิ่ม 7 tool ใหม่ตามที่คุยกันไว้ (ไม่มี dependency ใหม่เลย)
| Tool | Tier | หมายเหตุ |
|---|---|---|
| `system_status` | 0 | CPU% + uptime ผ่าน psutil |
| `network_status` | 0 | TCP connect 8.8.8.8:53 เช็คเน็ต |
| `clipboard_read` / `clipboard_write` | 0/1 | ดูข้อ 6.3 — เปลี่ยนวิธีทำหลังพบบั๊ก encoding |
| `media_control` | 1 | play/pause/next/prev ผ่าน VK media-key เหมือน `set_volume` |
| `set_timer` | 1 | background thread เตือนหลัง N นาที รูปแบบ args `"นาที|ข้อความ"` |
| `empty_recycle_bin` | 2 (confirm-gated) | ผ่าน shell32 `SHEmptyRecycleBinW` |

**Refactor ที่จำเป็น:** เดิม confirm-flow เขียนเฉพาะ `close_app` ตัวเดียว (`pending_close`) ตอนนี้มี 2 tool ต้อง confirm เลย generalize เป็น `pending_confirm` + dict `CONFIRM_GATED` (question/cancel/execute ต่อ tool) ใช้ร่วมกันได้ทั้งสองตัว

**เทสเต็มระบบด้วย LLM จริง** (`gemma4:31b-cloud` ผ่าน Ollama จริง ไม่ mock) — พูดคำสั่งภาษาธรรมดา 9 แบบ (รวม regression check ของ `close_app`) โมเดลเรียก tag ถูกทุกตัว 9/9 PASS

### 3. บั๊ก wording: โมเดลพูด "จัดการให้เรียบร้อยแล้ว" ก่อนขอยืนยันจริง
CEO ถามทวนแล้วพบว่าตัวระบบ **ไม่ได้ทำงานจริงจนกว่าจะยืนยัน** (โค้ดถูกอยู่แล้ว) แต่คำพูดของโมเดลก่อน tag `close_app`/`empty_recycle_bin` ทำให้เข้าใจผิดว่าทำไปแล้ว — แก้ด้วย instruction เพิ่มใน system prompt ห้ามพูดคำแปลว่าทำเสร็จนำหน้า 2 tag นี้ เทสซ้ำ 3 รอบกับ LLM จริง 6/6 ผ่าน ไม่มีคำหลอกอีก

### 4. เพิ่ม `CONFIRM_WORDS`: `เอาเลย`, `ปิดเลย`, `เค`

### 5. Bug fix 4 ข้อที่ CEO ฝากตรวจ (โค้ดรีวิวจากอ่านจริง ไม่ใช่แค่เดา)
1. **`speak()` ชนกันเอง** (main loop vs `set_timer` background thread — แย่งไฟล์ temp + pygame channel เดียวกัน) → เพิ่ม `AUDIO_LOCK` (threading.Lock) ครอบทั้ง generate+play+cleanup เทสจำลอง 2 thread เรียก `speak()` พร้อมกันจริง ยืนยันไม่ overlap
2. **Timer พูดแทรกตอนไมค์ฟังอยู่** → เพิ่ม `mic_listening` (threading.Event) set ตอน `r.listen()` จับเสียงจริง `speak()` เช็คก่อนพูดทุกครั้ง รอจนไมค์ปิดก่อน
3. **Clipboard ภาษาไทยเพี้ยน** (เดิมใช้ `clip.exe` ผ่าน stdin pipe เสี่ยง console codepage) → เปลี่ยนเป็น PowerShell `Set-Clipboard`/`Get-Clipboard` ผ่าน `-EncodedCommand` (base64 UTF-16LE) ข้าม codepage ไปเลย เทสจริงด้วยประโยคไทยยาว roundtrip ผ่านครบ
4. **`set_timer` ไม่ log เข้า vault** → เพิ่ม `log_to_vault()` ต่อจาก `speak()` ใน `_fire()`

รวมเทสหลังแก้ทั้งหมด: **27/27 PASS**

### 6. Session-file redesign (เปลี่ยนจากวันเดียวเป็น per-session ตาม Claude Code)
เริ่มจาก CEO สังเกตว่า history เก็บเป็นไฟล์ต่อวันไฟล์เดียว ถามว่านับ "session" (เปิด-ปิด = 1 session) ได้ไหม

**Iteration 1** (ถูก superseded แล้ว — ดูข้อสรุปด้านล่าง): ใส่ header `## Session N` คั่นในไฟล์รายวันเดิม + `backfill_session_markers()` แก้ไฟล์เก่าที่ไม่มี marker ให้เป็น Session 1 ย้อนหลัง

**เหตุผลที่เปลี่ยนใจ:** CEO ถามเทียบกับแบบ Claude Code (แยกไฟล์ต่อ session) วิเคราะห์ trade-off แล้ว:
- แยกไฟล์ต่อ session: ดึง/อ้างอิง session ล่าสุดง่าย (list ไฟล์ ไม่ต้อง parse header), คุมขนาด context ได้ง่าย — สำคัญเพราะ **CEO มีแผนแชร์ Friday ให้คนอื่นใช้ที่อาจรันโมเดลเล็ก context จำกัด** ถ้าวันหนึ่งมีฟีเจอร์โหลด session ก่อนหน้ามาต่อ context การจำกัดขนาดง่ายกว่าเยอะถ้าเป็นไฟล์แยก (โหลดแค่ N ไฟล์ล่าสุด) เทียบกับไฟล์รวมที่บวมขึ้นเรื่อยๆ
- ไฟล์รวมรายวัน + header: อ่านทั้งวันในที่เดียวง่ายกว่าใน Obsidian แต่แพ้ประเด็น context-bounding ด้านบน

**สรุป: ใช้ per-session file** — `vault/history/{date}_session-{NN}.md`

**ของปัจจุบัน (final):**
- `start_new_session()` — สแกนไฟล์ `_session-NN` ของวันนั้น หาเลขสูงสุด +1 สร้างไฟล์ใหม่ เขียน header `## Session N — เริ่ม HH:MM:SS`
- `log_to_vault()` — เขียนเข้าไฟล์ session ปัจจุบัน (ตัวแปร module-level `_current_session_path`) ถ้าเผลอเรียกก่อน `start_new_session()` จะ auto-start ให้เอง (lazy init)
- `migrate_legacy_day_files()` — ไฟล์เก่าสไตล์ `{date}.md` (ทั้งแบบดิบและแบบมี `## Session 1` header จาก iteration 1) เปลี่ยนชื่อเป็น `{date}_session-01.md` อัตโนมัติตอนเริ่มโปรแกรม ครั้งเดียว idempotent
- เรียกทั้งสองใน `main()`: `migrate_legacy_day_files()` แล้ว `session_number = start_new_session()` ก่อนทัก "สวัสดีค่ะนาย"

**รัน migration จริงแล้ว:** ไฟล์ `vault/history/2026-07-01.md` (บทสนทนาจริงของ CEO ตอนเช้า 10:29) → ย้ายเป็น `vault/history/2026-07-01_session-01.md` เนื้อหาครบ ไม่หาย (ตรวจแล้ว)

**Side-effect ที่เจอระหว่างเทสและแก้แล้ว:** รอบแรกๆ เทส `test_tools.py` (ทั้ง stub และตอนเปลี่ยนมารันด้วย env จริง `subtitle-aligner`) ทำให้เกิดไฟล์ session ปลอมในเครื่องจริงซ้ำหลายครั้ง (มาจาก `set_timer` self-check ที่ lazy-start session จริงเพราะยังไม่มี session เริ่มไว้) — ตอนแรกลองแก้ด้วย isolate HISTORY_DIR ชั่วคราวแล้วรอ 1.5s ให้ background thread ทำงานจบก่อนคืนค่า แต่ **ไม่พอกับ env จริง** เพราะ `speak()` เล่นเสียงจริงบล็อกได้หลายวินาที (นานกว่า TTS+cloud ปลอมตอน stub มาก) ทำให้ `log_to_vault()` หลุดไปเขียนหลังคืนค่า HISTORY_DIR แล้ว แก้จริงคือ **stub `fw.speak` เป็น no-op ไปเลยสำหรับเทสนี้** (เทสนี้สนใจแค่ timing/logging ไม่ใช่เสียงจริง) ยืนยันด้วยการรันซ้ำ 2 รอบกับ env จริง ไม่มีไฟล์หลุดอีกแล้ว

### 7. ตอบคำถาม day-boundary
ตัดวันเที่ยงคืนตาม `datetime.now()` = นาฬิกาของเครื่อง Windows ไม่ hardcode timezone ในโค้ด เครื่องนี้ตั้งเป็น SE Asia Standard Time (UTC+7 กรุงเทพฯ) — ถ้าย้ายเครื่อง/เปลี่ยน timezone จะตัดตามนั้นทันที

## ไฟล์ที่แก้/สร้างในช่วงนี้

- `friday_walkie_talkie.py` — เพิ่ม 7 tool, generalize confirm-gate, AUDIO_LOCK/mic_listening, clipboard ผ่าน PowerShell EncodedCommand, session-file system, CONFIRM_WORDS ใหม่ 3 คำ, prompt fix เรื่อง wording
- `friday_walkie_talkie.py.bak-20260701e` ถึง `.bak-20260701i` — backup แต่ละจุดก่อนแก้ใหญ่ (i = ล่าสุด ตรงกับโค้ด production ปัจจุบัน)
- `test_tools.py` — ขยายจาก 14 เป็น 29 check รวม audio-serialization, clipboard ไทย, session-file isolation tests
- `test_tools.py.bak-20260701e` ถึง `.bak-20260701i`
- `vault/history/2026-07-01_session-01.md` — migrate จากไฟล์เก่า (ข้อมูลจริงของ CEO)

## ถัดไป

1. ~~หา Python/venv ที่ CEO ใช้รันจริง~~ — **เจอแล้ว + แยก env ใหม่แล้ว** ใช้ `C:\Users\Win10\miniconda3\envs\friday\python.exe` (ดูข้อ 1 ด้านบน) เพิ่ม `psutil` เข้า `requirements.txt` ให้ตรงกับที่โค้ดใช้จริงแล้วด้วย
2. **CEO เทสผ่านไมค์จริงแบบเต็ม** — โฟกัสที่: 7 tool ใหม่ (โดยเฉพาะ `set_timer` ฟังเสียงเตือนจริง + `media_control` เปลี่ยนเพลงจริง), `empty_recycle_bin` confirm-flow (ยังไม่เคยรันจริงเลยสักครั้ง แม้แต่ตอน test เพราะเทสตั้งใจข้ามการรันจริง), คำยืนยันใหม่ (`เอาเลย`/`ปิดเลย`/`เค`)
3. **ตรวจ session-file ใหม่ตอนใช้งานจริงรอบหน้า** — เปิดโปรแกรม ควรเห็น `2026-07-01_session-02.md` ถูกสร้างใหม่ (ไฟล์ 01 คือของเช้านี้ที่ migrate มา — ไม่ใช่ไฟล์ทดสอบที่ผมสร้าง/ลบไปหมดแล้วในช่วงนี้)
4. เมื่อพร้อมเริ่ม Phase 2 (Connect agent) อ่าน handoff นี้ + [2026-07-01-toolset-hardening-and-roadmap.md](file:///D:/AI-Workspace/projects/jarvis/handoff/2026-07-01-toolset-hardening-and-roadmap.md) ก่อน — อย่าลืม confirm-before-send pattern ตามที่ระบุไว้ในนั้น

## ลงชื่อ

Commander (Claude) — session 2026-07-01
