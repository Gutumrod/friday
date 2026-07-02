---
path: D:\AI-Workspace\projects\jarvis\handoff\2026-07-02-safety-fixes-stress-test-and-hermes-audit-review.md
วันที่: 2026-07-02
ผู้เขียน: Commander (Claude)
---

# Handoff — 3 Safety Fix + ARM5 Stress-Test Methodology + Hermes Audit Review

ต่อจาก [2026-07-01-tools-hardening-p2-and-session-files.md](file:///D:/AI-Workspace/projects/jarvis/handoff/2026-07-01-tools-hardening-p2-and-session-files.md) เซสชันเดียวกัน (เริ่มค่ำวันที่ 1 ลากยาวข้ามเที่ยงคืนมาวันที่ 2 — เช็คแล้วด้วย `datetime.now()` จริง ไม่ใช่เดา) อ่านไฟล์นั้นก่อนถ้ายังไม่เห็น (7 tool ใหม่, session-file redesign, bug fix 4 ข้อรอบก่อน)

## สรุปสิ่งที่ทำในช่วงนี้

### 1. แก้บั๊ก confirm-gate-bypass (safety-critical)
พบว่า main loop เดิม (`tag_match = TOOL_PATTERN.search(reply)`) เช็ค**แค่แท็กแรก**ในคำตอบว่าเป็น confirm-gated tool หรือไม่ — ถ้า `close_app`/`empty_recycle_bin` ไม่ได้เป็นแท็กแรกในคำตอบที่มีหลายแท็ก จะตกไป `run_tools()` ซึ่งรันทุกแท็กจริงทันที **ข้าม confirm-gate ไปเลย**

**ใช้ ARM5 (Method Validation Gate จาก `D:/AI-Workspace/agents/claude/CLAUDE.md`) ตัดสินทางแก้** — ปรับเกณฑ์จาก "เร็วสุด" (ไม่เกี่ยวเพราะทุกทางรันไมโครวินาที) เป็น "ถูกต้องในเคสมุมๆ ≥2/3 + โค้ดง่ายสุด" หลัง CEO เห็นด้วย ทดสอบจริง 3 แนวทางกับ 6 เคสมุมๆ (`arm5_confirm_gate_test.py` ใน scratchpad):
- **A (เลือกใช้จริง)** — เจอ gated tag ที่ไหนก็ตาม → หยุดรันทุกแท็กในเทิร์นนั้น เหลือแค่ถามยืนยัน
- B (partial-execute) — ถูกต้องเท่า A แต่โค้ดซับซ้อนกว่า (mutate list ผ่าน closure ใน `re.sub`)
- C (first-tag-only) — **ตกรอบ** เพราะเคส "gated ไม่ใช่แท็กแรก" มันเงียบทิ้งคำสั่งไปเลย ไม่ถามด้วยซ้ำ (แย่กว่าบั๊กเดิมในมุมความน่าเชื่อถือ)

**แก้จริง:** เพิ่ม `find_first_gated_tag()` สแกนทุกแท็กหา CONFIRM_GATED ก่อนตัดสินใจ route (friday_walkie_talkie.py:491) — เทส regression ยิงตรงเคสบั๊กเดิม

### 2. Cloud-latency warning (เจอระหว่างเทส ไม่ได้ตั้งใจหา)
เทส 1(a) — ยืนยันว่า history-trim cap (system + 20 message ล่าสุด) กันบั๊ก "คุยจนตาย" ได้จริง (รัน 30 turn จริงกับ Ollama cloud, `history_len` ไม่เกิน 21 ตลอด, `total_chars` นิ่งที่ ~2,400 ตัวอักษร ห่างจาก `num_ctx=16000` มาก) — **ปิดเคสนี้ ไม่ต้องหา raw ceiling ต่อ**

แต่เจอ latency ต่อ turn แปรปรวนหนัก (ปกติ 1-3 วิ บางเทิร์นพุ่งถึง 8.9/13/17.5/**47.9 วิ**) ไม่เกี่ยวกับ context เลย เป็นความแปรปรวนฝั่ง Ollama cloud เอง — CEO สั่งให้เพิ่ม warning ถ้ารอเกิน 25 วิ ให้พูด **"ระบบ cloud มีปัญหา รอสักครู่นะคะนาย"** ก่อนจะ retry ต่อ (`ask_ollama()` friday_walkie_talkie.py:209-227) เทส regression ด้วย fake clock (ไม่ต้องรอจริง 25 วิ)

### 3. search_web content-safety fix (ร้ายแรงสุดที่เจอวันนี้)
เทสเรียก `tool_search_web("อากาศวันนี้")` ตรงๆ (คำค้นทั่วไปสุดๆ) เจอ**เนื้อหาโป๊หลุดมาจริง**ปนกับผลลัพธ์ — สาเหตุตรวจจาก source code จริงของ `ddgs`:
- `tool_search_web()` ไม่ระบุ `safesearch`/`backend` → ใช้ default `backend="auto"` ซึ่งกระจายไปหลาย engine
- engine `duckduckgo.py`, `bing.py`, `yahoo.py`, `wikipedia.py`, `yandex.py` **ไม่ใช้พารามิเตอร์ `safesearch` เลย** (โค้ดมี `# noqa: ARG002` = unused-argument ตั้งใจ) ต่อให้ตั้ง `safesearch="on"` ก็ไม่กรองอะไรจาก engine กลุ่มนี้
- คำค้นทั่วไป/high-volume โดน SEO keyword-stuffing จากเว็บสแปม/โป๊ตามที่รู้จักกันอยู่แล้ว

CEO ให้เกณฑ์ "ไม่ติดตราบใดที่ไม่หลุดเข้าลำโพง" → แก้ 2 ชั้น: (1) บังคับ `backend="google,brave,mojeek,startpage"` (engine ที่ยืนยันจาก source ว่าใช้ safesearch จริง) (2) `_EXPLICIT_KEYWORDS` deny-list กรองผลลัพธ์รายชิ้นก่อนส่งเข้า LLM สรุป เป็นด่านสุดท้ายก่อนถึงเสียงไม่ว่า engine จะหลุดหรือไม่ ยิงคำค้นเดิมซ้ำจริง → สะอาดแล้ว (กรมอุตุฯ, Windy, Google Play)

### 4. เจอ + ปิดเคส: Ollama bind 0.0.0.0
เช็ค `netstat` (ระหว่างวิเคราะห์ prompt-injection/external-attack surface) พบ Ollama proxy bind `0.0.0.0:11434`/`[::]:11434` เปิดรับทุก interface ไม่ใช่ localhost-only — รายงานไว้ ไม่ได้แก้เอง **CEO แก้เองแล้วนอกเซสชันนี้** ยืนยันด้วย `netstat` ซ้ำ ตอนนี้เหลือแค่ `127.0.0.1:11434` ปิดเคสแล้ว

### 5. ค้างไว้ยังไม่ทำ (ไม่ใช่ลืม ตัดสินใจพักไว้)
- **Native tool-calling ของ Ollama** — เช็ค `ollama show gemma4:31b-cloud` ยืนยันโมเดลรองรับ capability `tools` จริง เสนอย้ายจาก tag-parsing ไปใช้ native ก่อนเริ่ม Phase 2 (กัน confirm-gate ไปปะซ้อนกับ parser ที่จะเลิกใช้) — **ยังไม่ได้ทำ** รอ CEO ตัดสินใจ
- **Test 2 (set_timer stress)** — ออกแบบวิธีไว้แล้ว (escalate 10→100→1,000→10,000, stub speak(), วัด thread count/memory) CEO ถามความเสี่ยงก่อนรัน ผมแนะนำตัด ceiling เหลือ 1,000 (10,000 ไม่มี use case จริงรองรับ ได้แต่ความเสี่ยงหน่วงเครื่องจริง) **ยังไม่ได้ยืนยัน/รัน**
- **Test 3 (prompt-injection ผ่าน search_web)** — วิเคราะห์ attack surface แล้ว (ไม่มี network listener ในตัว Friday เอง, ช่องจริงคือ prompt injection ทางอ้อมผ่าน search results + audio injection ไม่มี wake-word/speaker verification) **ยังไม่ได้ทดสอบจริง**
- **UI (Golden HUD)** — CEO มี mockup + doc (`FRIDAY_UI_DESIGN.md`) แล้ว ตกลงกันว่าพักไว้แค่ออกแบบก่อน ไม่รีบทำ

### 6. รีเช็คระบบทั้งชุด 1 รอบ (ตามคำขอ CEO)
อ่านโค้ดจริงยืนยันครบ: loop หลัก, 16 tools, confirm-gate ใหม่, cloud-slow warning, search_web filter, Ollama bind — logic เข้ากันเป็นชิ้นเดียว ไม่มีจุดขัดกันเอง

### 7. รีวิว `audit/FRIDAY_AUDIT.md` ที่ Hermes ทำมา — เจอ 2 จุดที่ audit ผิด
- **B1 (psutil ขาดจาก requirements.txt)** — **ผิด** เช็คไฟล์จริงมี `psutil` อยู่แล้ว (เพิ่มไปตั้งแต่ตอนบ่ายแยก env `friday`) Hermes อาจอ่านไฟล์เก่า/cache
- **V3/B4 (open_web เปิด `file://` ได้)** — **ผิด** เช็คโค้ดจริง `tool_open_app`... ที่ถูกคือ `tool_open_web` เงื่อนไข `if query.startswith("http")` กันอยู่แล้ว — `file://...` ไม่ตรง prefix `"http"` เลยถูกยัดเป็นคำค้น Google แทน ไม่ได้เปิดไฟล์ตรง

**ของที่จริงและยังไม่ได้แก้:** V2/V6/B6 (`clipboard_read` ไม่ gate — privacy risk จริงถ้ามี password/OTP ในคลิปบอร์ด) — CEO ยังไม่ได้สั่งแก้ รอคิว

**เรื่อง dispatch_to_hermes (Phase 2 หัวใจ)** — Hermes เสนอต่อ mailbox ให้ Friday ส่งงานได้ ผมเสนอ contract 3 ข้อที่ต้องตกลงกับ Hermes ก่อนเขียนโค้ด (ยังไม่ได้ส่งให้ Hermes จริง รอ CEO ยืนยัน):
1. **Confirm-gate บังคับ** — ตาม standing rule เดิม (roadmap handoff บ่ายวันที่ 1) proposal ของ Hermes ไม่ได้พูดถึง ต้องเพิ่ม
2. **Round-trip แบบ blocking-poll-with-timeout** ในตัว tool เดียว (pattern เดียวกับ `search_web` ที่มีอยู่แล้ว) — ไม่ต้องรอ Phase 3 (VAD/async) เลย
3. **Mailbox result format** — ฝั่งส่งรู้แล้ว (`mailbox_utils.py create --to Hermes`) แต่ยังไม่รู้ Hermes จะเขียนผลกลับที่ไหน/format ไหนให้ Friday poll อ่านได้ — ต้องถาม Hermes ให้ชัดก่อน

## ไฟล์ที่แก้/สร้างในช่วงนี้

- `friday_walkie_talkie.py` — `find_first_gated_tag()` ใหม่ + main loop routing fix, `ask_ollama()` เพิ่ม cloud-slow warning, `tool_search_web()` เพิ่ม backend restriction + `_EXPLICIT_KEYWORDS` filter
- `friday_walkie_talkie.py.bak-20260701j/k/l` — backup ก่อนแก้แต่ละจุด (3 จุดข้างต้น)
- `test_tools.py` — เพิ่ม 4 เทส (`gated_tag_scan(not_first)`, `ask_ollama(slow_warning)`, `search_web_filters_explicit`, `search_web_all_results_explicit`) รวมเทสทั้งหมดตอนนี้ **33/33 PASS**
- `test_tools.py.bak-20260701k/l/m`
- Scratchpad (ไม่ใช่ในโปรเจกต์ ลบได้): `arm5_confirm_gate_test.py`, `test1a_context_cap_confirm.py` — ใช้ตัดสินทางแก้บั๊ก #1 และยืนยัน context cap เก็บไว้เป็นหลักฐานอ้างอิงถ้าต้องย้อนดู

## ถัดไป

1. **ตัดสินใจเรื่อง native tool-calling** — ย้ายจาก tag-parsing ไปใช้ Ollama native `tools` API (โมเดลรองรับแล้ว, เช็คแล้วจริง) แนะนำทำก่อนเริ่ม dispatch_to_hermes เพื่อไม่ต้องปะ confirm-gate ซ้อนกับ parser ที่จะเลิกใช้
2. **ตอบ Hermes เรื่อง contract 3 ข้อ** สำหรับ `dispatch_to_hermes` — รอ CEO ยืนยันให้ส่งกลับไปทาง mailbox
3. **แก้ clipboard_read gate** (V2/V6/B6 จาก audit) — ง่าย เร็ว รอคิว CEO สั่ง
4. **Test 2/3 ที่พักไว้** — set_timer stress (รอ CEO ยืนยัน ceiling 1,000 หรือ 10,000), prompt-injection test (ออกแบบไว้แล้ว ปลอดภัย พร้อมรันได้ทันทีที่สั่ง)
5. เมื่อพร้อมเริ่ม Phase 2 เต็มรูป อ่าน handoff นี้ + [2026-07-01-tools-hardening-p2-and-session-files.md](file:///D:/AI-Workspace/projects/jarvis/handoff/2026-07-01-tools-hardening-p2-and-session-files.md) + [2026-07-01-toolset-hardening-and-roadmap.md](file:///D:/AI-Workspace/projects/jarvis/handoff/2026-07-01-toolset-hardening-and-roadmap.md) ก่อน — อย่าลืม confirm-before-send pattern

## ลงชื่อ

Commander (Claude) — session 2026-07-01/02 (ข้ามเที่ยงคืน)
