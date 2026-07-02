---
path: D:\AI-Workspace\projects\jarvis\handoff\2026-07-01-toolset-hardening-and-roadmap.md
วันที่: 2026-07-01
ผู้เขียน: Commander (Claude)
---

# Handoff — Friday: 9-Tool Standalone Toolset + Re-planned Roadmap

ต่อจาก [2026-07-01-memory-vault-and-numctx-fix.md](file:///D:/AI-Workspace/projects/jarvis/handoff/2026-07-01-memory-vault-and-numctx-fix.md) เซสชันเดียวกัน คนละช่วง — อ่านไฟล์นั้นก่อนถ้ายังไม่เห็น (persona, memory vault, num_ctx fix)

## สรุปสิ่งที่ทำในช่วงนี้

### 1. True purpose ของโปรเจกต์ (สำคัญที่สุด)
CEO ยืนยันชัดเจน: Friday ไม่ใช่แค่ voice chatbot แต่ตั้งใจให้เป็น **meta-agent ที่คุมเอเจนตัวอื่น** (Hermes, OpenClaw) ผ่านเสียง — "ให้เป็นเอเจนที่คุมเอเจนอีกที" นี่คือ north star ของทุก decision ต่อจากนี้ ไม่ใช่แค่ utility tool เล่นๆ

### 2. Toolset — ตอนนี้มี 9 tool (ผ่าน `[TOOL: name(args)]` tag-parsing, ไม่ใช่ Ollama native tool-calling — เลือกแบบ tag เพราะ CEO สั่ง "เบื้องต้นก่อน" แต่ implementation ยังต้องได้มาตรฐาน ไม่ใช่ลวกๆ)

| Tool | ทำอะไร | หมายเหตุความปลอดภัย/robustness |
|---|---|---|
| `get_time` | บอกเวลา/วันที่ | - |
| `disk_space` | เช็คพื้นที่ดิสก์ C | - |
| `open_app` | เปิดแอป | **Allowlist เท่านั้น** (`ALLOWED_APPS` dict) — notepad, calculator, explorer, chrome, capcut — path ทุกตัว verify ว่ามีจริงในเครื่องก่อนใส่ ไม่เดา |
| `close_app` | ปิดแอป (taskkill /F) | **ต้องยืนยันก่อนทำจริง** (ดูข้อ 3) + guard พิเศษกัน "explorer" (คือ shell/desktop ไม่ใช่แอปทั่วไป ปิดแล้วจอรวน) |
| `set_volume` | ปรับเสียงขึ้น/ลง/mute | ผ่าน `ctypes` native (VK_VOLUME_*) ไม่มี dependency ใหม่ — ปรับได้แค่ relative step ไม่ใช่ % แน่นอน (ต้อง pycaw ถ้าจะทำ % จริง ยังไม่ทำ) |
| `list_processes` | Top 5 process กินแรมสุด | ผ่าน `psutil` (มีอยู่แล้วในเครื่อง) — มีแค่ RAM ไม่มี CPU% (CPU sampling ต้องหน่วงรอ interval เลยข้ามไปก่อน) |
| `open_web` | เปิดเบราว์เซอร์ไป URL/ค้นหา | แค่เปิด ไม่อ่านผลกลับ |
| `remember` | จดข้อความลง `vault/facts.md` | **มี dedup** — เช็คว่ามีข้อความเดียวกันอยู่แล้วก่อนเขียนซ้ำ |
| `search_web` | ค้น DuckDuckGo แล้วสรุปคำตอบให้ฟัง | ใช้ `ddgs` (ติดตั้งใหม่, ไม่ใช่ `duckduckgo_search` เก่า) — **มี retry 3 ครั้ง** กัน DDG rate-limit (ไม่มี API key เลยโดน limit ง่าย) — ตัวเดียวที่ยิง Ollama 2 รอบ (ค้น→สรุป) ตัวอื่นทั้งหมด splice คำตอบทันทีรอบเดียว |

### 3. Confirm-before-execute (เฉพาะ close_app)
วิเคราะห์แล้วว่าไม่ควรบังคับยืนยันทุก tool (ขัดกับนิสัยที่ตั้งไว้ว่าตอบเร็วไม่พร่ำเพรื่อ + tool ส่วนใหญ่ไม่เสี่ยง/แก้คืนง่าย) — มีแค่ `close_app` ตัวเดียวที่เสี่ยงจริง (`taskkill /F` ไม่ถามเซฟงาน อาจทำงานที่ยังไม่เซฟหายได้) เลยทำ confirm flow เฉพาะตัวนี้:

- Friday เจอ `[TOOL: close_app(...)]` → **ไม่รันทันที** → ตั้ง `pending_close = app_name` แล้วพูดถามยืนยันแทน
- Turn ถัดไป: ถ้าคำตอบอยู่ใน `CONFIRM_WORDS` (ใช่/ยืนยัน/ตกลง/โอเค ฯลฯ) → รันจริง / ถ้าไม่ใช่ → ยกเลิก แล้วเอาคำพูดนั้นไปประมวลผลเป็นคำสั่งใหม่ต่อ (ไม่ทิ้งไปเฉยๆ)
- Logic นี้ยังไม่ได้ทดสอบผ่านไมค์จริงแบบ end-to-end (unit test ผ่านแล้วแค่ regex/state logic) — **CEO บอกจะกลับไปเทสเอง**

### 4. Roadmap ใหม่ (แทนที่ลำดับเดิมใน PRD.md)
CEO บอกลำดับเดิมจาก Antigravity "ยุ่งเหยิง" เลยจัดใหม่ร่วมกัน:

1. ✅ **Harden ของเดิมให้แข็งแรง** (ทำในช่วงนี้ — retry, dedup, allowlist ขยาย, confirm flow, tool ใหม่)
2. ⬜ **Connect agent** — Hermes mailbox dispatch (`send_to_hermes` tool ผ่าน `mailbox_utils.py create`) **และ/หรือ** พิมพ์ Telegram ในนาม CEO เอง (ไม่ใช่บอท — ต้องใช้ Telethon, login ด้วยเบอร์จริง, ได้ session file ที่เท่ากับกุญแจเข้าบัญชีเต็มรูปแบบ ต้องเก็บให้ปลอดภัยจริงจัง ยังไม่มีการตั้งค่าใดๆ ตอนนี้)
3. ⬜ **Interrupt (VAD, Gemini Live style)** — สลับลำดับมาก่อน local-first ตามที่ CEO ขอ
4. ⬜ **Local-first (offline STT/TTS)** — CEO ขอให้อยู่ท้ายสุด เพราะต้องหา Thai TTS ที่เวิร์คจริงก่อน (ChindaTTS by iApp เป็นตัวเลือกที่สำรวจไว้ — Kaitom/Kaimook เสียง, ราคา 1 credit/400 ตัวอักษร มี 50 credit ฟรี ยังไม่ได้ตัดสินใจใช้)

**คำเตือนสำคัญสำหรับ Phase "Connect agent":** เมื่อทำ `send_to_hermes` ต้องมี confirm-before-send เหมือน `close_app` เพราะเป็น tool แรกที่มีผลกระทบนอกเครื่อง (เขียนเข้า mailbox จริงที่ Hermes เห็น) — mishear/hallucinate อาจส่งงานผิดกวนทีมได้ ห้ามข้าม safety pattern นี้

### 5. Standing rule ที่ CEO ย้ำไว้ (สำคัญ ต้องคงไว้ทุก session ถัดไป)
- "ทำง่ายๆ" = จำกัด**ขอบเขต** เท่านั้น ห้ามใช้เป็นข้ออ้างข้าม error handling / test / security ของสิ่งที่ทำจริง (ดู [[feedback_lazy_scope_not_lazy_quality]])
- ทำงานเสร็จแต่ละชิ้น **อย่ารีบเสนอ next step ทันที** ปล่อยให้ CEO กำหนดจังหวะเอง (ดู [[feedback_dont_rush_next_step]])
- ทุกครั้งที่แก้โค้ดมีผล backup ก่อนเสมอ (ดูไฟล์ `.bak-*` ในโฟลเดอร์โปรเจกต์ ถ้าต้อง rollback)

## ไฟล์ที่แก้/สร้างในช่วงนี้

- `friday_walkie_talkie.py` — เพิ่ม 4 tool ใหม่ (close_app, set_volume, list_processes รวมกับที่มีอยู่), hardening (retry/dedup/allowlist ขยาย), confirm-flow
- `friday_walkie_talkie.py.bak-20260701b/c/d` — backup แต่ละจุดก่อนแก้ใหญ่
- `requirements.txt` — เพิ่ม `ddgs>=9.14.4`
- `vault/facts.md` — ล้างข้อมูลทดสอบออกแล้ว เหลือแต่ของจริง
- Memory (Claude): อัปเดต [[project_jarvis_friday_walkie_talkie]], [[reference_dispatch_hermes_openclaw]] (แก้ให้ตรงกับ Mailbox v2), เพิ่ม [[feedback_dont_rush_next_step]], [[feedback_lazy_scope_not_lazy_quality]]

## ถัดไป

รอ CEO เทส `close_app` confirm-flow ผ่านไมค์จริงก่อน แล้วค่อยเริ่ม Phase 2 (Connect agent) — ตอนเริ่ม อ่าน handoff นี้ + [[reference_dispatch_hermes_openclaw]] (schema `mailbox_utils.py create` ปัจจุบัน) ก่อนเขียนโค้ด อย่าลืม confirm-before-send pattern

## ลงชื่อ

Commander (Claude) — session 2026-07-01
