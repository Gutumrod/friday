---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-02-github-init-and-timer-killprocess-verify.md
วันที่: 2026-07-02
ผู้เขียน: Commander (Claude)
---

# Handoff — GitHub repo init + push, set_timer kill-process ยืนยันจริง, ย้ายเครื่อง

ต่อจาก [2026-07-02-latency-phase1-timer-resilience-jarvis-warning.md](2026-07-02-latency-phase1-timer-resilience-jarvis-warning.md) — เซสชันใหม่ วันเดียวกัน อ่านไฟล์นั้นก่อนถ้ายังไม่เห็น (Phase 1 latency, set_timer resilience design, จาวิส warning voice)

**เหตุผลที่มี handoff นี้:** CEO กำลังจะย้ายเครื่อง คุยกันแล้วว่าแชท/session ของ Claude Code ไม่ตามไปเครื่องใหม่อัตโนมัติ (ต่างเครื่อง ต่าง `~/.claude/`) — handoff ไฟล์นี้ (ที่ push ขึ้น GitHub แล้ว) คือกลไกหลักให้ Claude เซสชันใหม่บนเครื่องใหม่ตามทันสถานะโปรเจกต์ อ่านไฟล์นี้ + ไฟล์ก่อนหน้าให้ครบก่อนทำงานต่อ

## สรุปสิ่งที่ทำในเซสชันนี้

### 1. ยืนยัน set_timer kill-process จริง (ปิดจากรายการ "ยังไม่ได้ทำ" ใน handoff ก่อนหน้า)
ทดสอบจริง ไม่ใช่แค่ทฤษฎี: เขียน driver script เรียก `tool_set_timer("0.5|kill-process-test")` ตรงๆ (ไม่ผ่านไมค์ — pattern เดียวกับที่เคยเทส open_app/close_app), เช็คว่า backup Scheduled Task ลงทะเบียนจริง (`Get-ScheduledTask`), **force-kill process** ตอนนับถอยหลังไปได้ ~10 วิ จาก 30 วิ (`Stop-Process -Force`), แล้ว poll จนกว่า task หาย ยืนยันด้วย `vault/history/2026-07-02_session-05.md` (session ใหม่จาก process ใหม่ที่ `fire_reminder.py` สร้าง) มีข้อความเตือนจริง + scheduled task ลบตัวเองสำเร็จ ไม่มีอะไรค้าง

**สรุป:** ฟีเจอร์นี้ verified ครบ 100% แล้ว ไม่ใช่ความเชื่อมั่นทางทฤษฎีอีกต่อไป

### 2. Git init + push ขึ้น GitHub (โปรเจกต์นี้ไม่เคย git มาก่อน)
CEO ตัดสินใจ: **public repo**, ไม่เอา `vault/` ขึ้น (ข้อมูลส่วนตัว) — เหตุผลย้ายเครื่อง

- `.gitignore`: `__pycache__/`, `*.pyc`, `src/tts_cache/`, `voices/`, `vault/`, `backups/`
- Repo: **https://github.com/Gutumrod/friday** (public) — commit แรก `3d4ea92` มี 20 ไฟล์ (src/docs/handoff/audit/requirements.txt) เช็คแล้วไม่มี API key/secret ฝังในโค้ด (Ollama เรียกผ่าน `localhost:11434` เท่านั้น)
- `gh auth login` — CEO ทำเองผ่าน browser (device code), ยืนยันแล้ว `gh auth status` = logged in as `Gutumrod`
- Push สำเร็จ, verified: `git status --short` ว่าง (ไม่มีอะไรค้าง commit), GitHub API `contents` ตรงกับของในเครื่อง

**สิ่งที่ตั้งใจไม่เอาขึ้น git และทำไมไม่กระทบการรันบนเครื่องใหม่ (เช็คโค้ดแล้ว ไม่ได้เดา):**
- `vault/` — `main()` เรียก `migrate_legacy_day_files()` ซึ่ง `os.makedirs(HISTORY_DIR, exist_ok=True)` สร้างให้เองตอนรันครั้งแรก, `load_facts()` คืนค่าว่างถ้าไม่มีไฟล์ ไม่ error
- `voices/th_f_1.onnx` (61MB) — ไม่ได้ผูก path ตรงในโค้ด เป็น cache ที่ `pythaitts` (`TTS(pretrained="vachana")`) โหลดเองตอนใช้ fallback TTS ครั้งแรก จะโหลดใหม่อัตโนมัติ (ช้าแค่ครั้งแรก)
- `backups/`, `src/tts_cache/` — ไม่จำเป็นต้องมีตอนรันเลย

**ข้อควรรู้สำหรับ CEO เรื่องย้ายเครื่อง (คุยกันแล้วในแชท ไม่ได้บันทึกไว้ที่อื่น):**
- `vault/` (facts.md + ประวัติสนทนา) **ไม่ sync ผ่าน git โดยตั้งใจ** — ถ้าอยากให้ Friday จำเรื่องเก่าต่อบนเครื่องใหม่ ต้อง copy โฟลเดอร์นี้มือ (USB/Drive) แยกจาก git ไม่งั้น Friday จะเริ่มความจำใหม่หมดบนเครื่องใหม่ (กลายเป็นคนละตัวความจำคนละชุด)
- Workflow สองเครื่อง: `git pull` ก่อนเริ่มงานทุกครั้ง, `git push` ก่อนออกจากเครื่องนั้น, **อย่าแก้พร้อมกันสองเครื่อง** (จะชน merge conflict)
- ตั้งเครื่องใหม่: `git clone https://github.com/Gutumrod/friday.git` → `conda create -n friday python=3.10 -y` → `pip install -r requirements.txt` → รัน `python src/friday_walkie_talkie.py` จาก root โปรเจกต์

## ทดสอบ
51/51 (`test_tools.py`) ยังผ่านเหมือนเดิม ไม่ได้แก้โค้ดฟังก์ชันในเซสชันนี้ (แค่ verify + git infra) + kill-process live test ผ่านตามข้อ 1

## ค้างจากก่อนหน้า (ยังไม่เปลี่ยนสถานะ — ดูรายละเอียดเต็มใน handoff ก่อนหน้า)

- **CEO ทดสอบพูดจริงผ่าน full voice pipeline** ("เปิด Notepad" ด้วยเสียงจริง) — ยังไม่ได้ทำ, Commander ไม่มีไมค์
- ตอบ Hermes เรื่อง contract 3 ข้อสำหรับ `dispatch_to_hermes` — รอ CEO ยืนยันเนื้อหา (สรุป 3 ข้อ: confirm-gate บังคับ, blocking-poll-with-timeout pattern เดียวกับ search_web, ต้องถาม Hermes เรื่อง mailbox result format)
- Test 2 (set_timer stress escalation) — รอ CEO ยืนยัน ceiling (1,000 หรือ 10,000)
- ~~แก้ `clipboard_read` gate~~ — **แก้ไปแล้วจริง** ตั้งแต่ตอนทำ tiered confirm-gate วันนี้ (อยู่ใน `CONFIRM_GATED` แล้ว มี wiring test `check_clipboard_read_wiring` ผ่าน) รายการนี้เป็นของค้างที่หลุดมาจาก handoff เก่าตอนเช้า อย่าหยิบมาทำซ้ำ
- Wake word / voiceprint แท้ๆ — พักไว้
- Phase 3 (streaming Ollama response + sentence-chunked TTS) — ยังไม่เริ่ม เสี่ยงกระทบ `CONFIRM_GATED`
- Phase 4 (VAD/interruptible barge-in, local model แทน cloud, wake word) — พักไว้
- Telegram integration — ยังไม่เริ่ม (reminder รอดจากปิดเครื่องทั้งเครื่อง รอ Phase นี้ + `dispatch_to_hermes`)

## ลงชื่อ

Commander (Claude) — session 2026-07-02 (ต่อจากเซสชัน latency/timer เช้า-บ่ายวันเดียวกัน)
