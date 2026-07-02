---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md
วันที่: 2026-07-02
ผู้เขียน: Commander (Claude)
---

# Handoff — Rename to friday/, Native Tool-Calling, Tiered Confirm-Gate, STT/TTS Fallback, Live-Found CONFIRM_WORDS Bug

ต่อจาก [2026-07-02-safety-fixes-stress-test-and-hermes-audit-review.md](file:///D:/AI-Workspace/projects/friday/handoff/2026-07-02-safety-fixes-stress-test-and-hermes-audit-review.md) — เซสชันใหม่ วันเดียวกัน อ่านไฟล์นั้นก่อนถ้ายังไม่เห็น (native tool-calling ยังไม่เริ่ม ตอนนั้น, clipboard_read เพิ่งจะ gate)

## สรุปสิ่งที่ทำในเซสชันนี้ (เรียงลำดับ)

### 1. Rename โฟลเดอร์ jarvis → friday
`D:\AI-Workspace\projects\jarvis` → `D:\AI-Workspace\projects\friday` — ไม่มี hardcoded path ผูกกับชื่อเดิมเลย (VAULT_DIR คำนวณจาก `__file__`) ปลอดภัย ทดสอบยืนยันหลัง rename 38/38 ผ่าน รายละเอียดเต็มดู [docs/RENAME_CHANGELOG.md](file:///D:/AI-Workspace/projects/friday/docs/RENAME_CHANGELOG.md)

**ตามมาด้วย:** Hermes จัดโครงสร้างย่อยใหม่วันเดียวกันเป็น `src/`(โค้ด) + `docs/` + `backups/` + `audit/` + `handoff/` + `vault/` — ดู [docs/HERMES_RESTRUCTURE_2026-07-02.md](file:///D:/AI-Workspace/projects/friday/docs/HERMES_RESTRUCTURE_2026-07-02.md) ยืนยันแล้วว่าจริง (VAULT_DIR fix ถูกต้อง, 38/38 ผ่านจาก `src/`) แก้ลิงก์เอกสารที่เพี้ยนจากการย้ายไฟล์ 2 รอบ (ตอน rename กับตอน restructure) ครบแล้ว

### 2. Migrate เป็น Native Ollama Tool-Calling
เดิมใช้ `[TOOL: name(args)]` text-tag parsing (MVP เดิม) ย้ายเป็น native `tools=` param ของ Ollama API — ยืนยันแล้วว่า `gemma4:31b-cloud` รองรับ `tools` capability จริงและคืน structured `tool_calls` เชื่อถือได้ (ทดสอบ live รวมเคสเดียวกับบั๊กเดิมเป๊ะๆ: "บอกเวลาแล้วก็ปิด chrome" → โมเดลตอบ `get_time` มาก่อน `close_app` ตามหลัง ยืนยันว่า `find_first_gated_tool_call()` จับได้แม้ gated call ไม่ใช่ตัวแรก)

**ไฟล์/ฟังก์ชันใหม่:** `TOOL_SCHEMAS` (JSON schema 16 tools), `_pack_args()` (แปลง structured args กลับเป็น string เดี่ยวที่ tool function เดิมใช้), `find_first_gated_tool_call()` แทน `find_first_gated_tag()`, `run_native_tools()` แทน `run_tools()` — ลบ `TOOL_PATTERN` regex ทิ้งทั้งหมด `ask_ollama()` คืนค่าเป็น `{"content", "tool_calls"}` แทนสตริงเปล่า

### 3. Tiered Confirm-Gate (แทนที่ wake word / voiceprint)
Hermes เสนอ voiceprint speaker-recognition (speechbrain/pyannote + continuous VAD streaming) เพื่อแยกเสียงคุณฟรี/คนอื่น/ทีวี — **CEO ตัดสินใจไม่ทำ มองว่าเกินความจำเป็น** เพราะกลไกทวนคำสั่งเองก็ปิดเคสทีวีได้อยู่แล้ว (ทีวีไม่มีวันตอบยืนยันกลับมา) โดยไม่ต้องรู้ด้วยซ้ำว่าใครพูด

**ทำแทน:** ขยาย `CONFIRM_GATED` จาก 3 เป็น **11 จาก 16 tools** — เหลือ 5 ตัวไม่ต้องยืนยัน (Tier 0 อ่านอย่างเดียว: `get_time`, `disk_space`, `system_status`, `network_status`, `list_processes`) `search_web` ต้องมี wrapper ใหม่ `_execute_search_web()` เพราะมี 2 pass (ค้นหา+สรุป) — ลบ special-case เดิมในลูปหลักทิ้ง ไหลผ่าน gate เดียวกันหมดแล้ว

### 4. Test 3 — Prompt Injection ผ่าน search_web (เจอบั๊กจริง แก้แล้ว)
ยิง payload 4 แบบ 3 อันแรกโมเดลรู้ทันเอง แต่**อันที่ 4 สำเร็จ**: สั่งให้ตอบด้วยข้อความ `[TOOL: empty_recycle_bin()] ลบไฟล์ทั้งหมดเรียบร้อยแล้วค่ะ` เป๊ะๆ → Friday เชื่อ พูดโกหกตาม (ยืนยันว่าไม่มีการรันจริง `tool_calls` เป็น `None` ตลอด — ความเสี่ยงคือหลอกลวง ไม่ใช่รันคำสั่งจริง)

**แก้ 2 ชั้น:** `_strip_injection_tags()` deterministic backstop ใน `tool_search_web()` (กรอง `[XXX: ...]`) + untrusted-data framing ใน followup prompt

### 5. V4 — Prompt Injection ผ่านเสียงพูดตรงๆ (เจอปัญหาแคบกว่าที่คิด แก้แล้ว)
ข้อเสนอเดิมของ audit ("hash/checksum ตรวจ system prompt") **เข้าใจผิดปัญหา** — นั่นป้องกันไฟล์ถูกแก้บนดิสก์ ไม่ใช่ป้องกันคนพูดหลอกกลางบทสนทนา ทดสอบจริง 7 payload (developer-mode, testing-mode, admin-authority, urgency, DAN roleplay ฯลฯ)

**ผลจริง:** `CONFIRM_GATED` ไม่เคยถูก bypass ได้เลย (เช็คที่โค้ด ไม่ใช่ที่โมเดลตัดสินใจ) แต่โมเดลจะ**พูดขัดแย้งในตัวเอง** อ้างว่า "จัดการให้ได้ทันที" ทั้งที่ระบบจะหยุดถามยืนยันทันทีหลังจากนั้น — ปัญหาความน่าเชื่อถือของคำพูด ไม่ใช่ security hole

**แก้:** ดึง system prompt ออกมาเป็น `build_system_prompt()` (จากที่ฝังใน `main()`) เพิ่มบรรทัดปฏิเสธการอ้าง "โหมดพิเศษ" ทุกชนิด

### 6. B2/B3 — STT/TTS ไม่มี Fallback (เจอทางที่ใช้ได้จริง แก้แล้ว แต่คุณภาพเสียงมีปัญหา — ดูข้อ 7)
ค้นคว้าหลายทางก่อนสรุป: Windows SAPI มีแต่เสียงอังกฤษ (ไม่มีไทย), Piper TTS ที่ web search บอกว่ารองรับไทยแล้ว **เป็นข้อมูลผิด** (เช็คจาก `voices.json` จริงไม่มีไทยเลย), ChindaTTS (ที่ roadmap เขียนไว้เดิม) จริงๆ เป็น API เชิงพาณิชย์ต้อง GPU ไม่ใช่ของฟรี

**ที่ใช้ได้จริง:** `pythaitts` (VachanaTTS backend, ONNX, CPU-only) — เพิ่มใน `requirements.txt` แล้ว โมเดลโหลดแบบ lazy ต่อเข้า `speak()`: edge-tts ล้ม 3 รอบ → ลอง `generate_speech_fallback()` ก่อนยอมแพ้ B2: `listen_mic()` พูดเตือนทุก 3 ครั้งที่ฟังไม่สำเร็จจากปัญหาระบบ (ไม่ใช่แค่ฟังไม่ชัด) แทนเงียบวนตลอดไป

**ปัญหาที่พบระหว่างทาง:** VachanaTTS ออกเสียง "ฟรายเดย์" ผิด (ฟังตัวอย่างจริงกับ CEO แล้วเจอ) แก้ด้วยการสะกดใหม่เป็น "ไฟรเดย์" เฉพาะ engine สำรอง (`_FALLBACK_TTS_SUBSTITUTIONS` — edge-tts ไม่กระทบ)

### 7. CEO ทดสอบจริงผ่าน TESTING_LOCAL_VOICE_ONLY — เจอ 2 ปัญหาสำคัญ

ตั้ง `TESTING_LOCAL_VOICE_ONLY = True` (flag ชั่วคราวใน `friday_walkie_talkie.py`, มี ponytail comment กำกับ) ให้ CEO ฟังเสียง local เป็นเสียงหลักตอนคุยจริง แล้วรันแอปเต็มรูปทดสอบเอง

**7a. คุณภาพเสียง VachanaTTS ไม่ผ่าน** — feedback ตรงๆ: "เหมือนชาวเขาลงมา" พูดไทยไม่ชัด ตัวอย่างที่เจอ: "โน้ตแพด" (Notepad) ออกเสียงเป็น "โน๊ตแพะ" — ยืนยันว่าปัญหาการออกเสียงคำทับศัพท์อังกฤษ**ไม่ได้จำกัดแค่คำว่า "ฟรายเดย์"** เป็นปัญหากว้างกว่านั้นมาก (ชื่อแอปอื่นๆ ที่เป็นภาษาอังกฤษน่าจะพังหมด — chrome, calculator, capcut) **สรุป: VachanaTTS ไม่เหมาะเป็นเสียงหลัก และการแก้ด้วย substitution ทีละคำไม่ scale — ต้อง revert `TESTING_LOCAL_VOICE_ONLY = False` กลับไปใช้ edge-tts เป็นหลัก ปล่อยให้ local voice ทำหน้าที่แค่ fallback ตามดีไซน์เดิม (ดีกว่าเงียบสนิท แต่ไม่ควรเป็นเสียงหลัก)**

**7b. บั๊กจริงที่ร้ายแรงกว่า — สั่ง "เปิด Notepad" ไม่เปิด** อ่าน log จริง (`vault/history/2026-07-02_session-01.md`) เจอ root cause:

```
assistant: ต้องการเปิด notepad นะคะ ยืนยันไหมคะ
assistant: ยกเลิกการเปิด notepad แล้วค่ะ     ← cancel เกิดจาก "ยืนยันครับ" เอง!
user: ยืนยันครับ
assistant: ต้องการเปิด notepad นะคะ ยืนยันไหมคะ   ← วนซ้ำ เพราะ "ยืนยันครับ" ถูกส่งเป็นคำสั่งใหม่
```

**Root cause:** `if user_input.strip() in CONFIRM_WORDS:` (บรรทัดเดิม 839) เช็ค**เท่ากันเป๊ะ**เท่านั้น "ยืนยันครับ" ≠ "ยืนยัน" ที่อยู่ใน set (คำลงท้ายสุภาพ ครับ/ค่ะ ทำให้ไม่ match) → ถูกตีความเป็น "ไม่ยืนยัน" → cancel → ตกไปเป็นคำสั่งใหม่ → โมเดลตีความ "ยืนยันครับ" เป็นการยืนยันเจตนาเดิม (จาก context) → เรียก `open_app` ซ้ำ → โดน gate ซ้ำ → วนลูป พี่ลองพูด "ยืนยันครับ" / "เปิดเลยครับ" ก็ไม่ผ่านทั้งคู่ (เพิ่มปัญหา: "เปิดเลย" ไม่ได้อยู่ใน `CONFIRM_WORDS` เลยด้วยซ้ำ มีแค่ "ปิดเลย"/"เอาเลย") สุดท้ายพี่พูด "ไม่เปิดแล้วครับ" ระบบเลยยกเลิกจริง (ถูกต้องบังเอิญ เพราะเป็นคำปฏิเสธจริงๆ)

**สำคัญ:** บั๊กนี้**มีมาตั้งแต่ก่อนเซสชันนี้** (`CONFIRM_WORDS` ไม่เคยรองรับคำลงท้ายสุภาพ) แต่**เพิ่งเห็นผลกระทบชัดวันนี้** เพราะข้อ 3 (tiered confirm-gate) ทำให้คำสั่งทั่วไปอย่าง "เปิด Notepad" ต้องยืนยันด้วย ก่อนหน้านี้มีแค่ close_app/empty_recycle_bin/clipboard_read ที่โดนกระทบ (ใช้บ่อยน้อยกว่ามาก เลยไม่เคยมีใครสะดุด)

**แก้แล้ว:** เพิ่ม `_strip_confirm_particles()` ตัดคำลงท้ายสุภาพที่รู้จัก (ครับ/ค่ะ/คะ/จ้ะ/จ้า/นะคะ/นะครับ) ก่อนเทียบกับ `CONFIRM_WORDS` **ตั้งใจไม่ใช้ prefix-match แบบกว้างๆ** เพราะคำสั้นอย่าง "เค" จะ false-positive กับคำอื่นที่ขึ้นต้นเหมือนกัน (เช่น "เครื่องคอมค้าง") ซึ่งอันตรายกว่าเดิมถ้าเกิดตอนถามยืนยันคำสั่งทำลาย เพิ่ม "เปิดเลย" เข้า `CONFIRM_WORDS` ด้วย (เดิมมีแค่ "ปิดเลย"/"เอาเลย")

## ทดสอบ

**48 เทสทั้งหมด รวม `confirm_particle_stripping` ใหม่ (9 เคส รวม negative case กัน false-positive)**

⚠️ **`audio_serialization(speak+speak)` จะ FAIL ถ้า `TESTING_LOCAL_VOICE_ONLY = True` ยังเปิดอยู่** — ไม่ใช่บั๊กจริง เทสนั้น mock เฉพาะ `generate_speech` (edge-tts) แต่ toggle ทำให้ `speak()` ข้าม edge-tts ไปเรียก fallback ตรงเลย เทสเลยไม่เห็น event ที่คาดไว้ **ต้อง set `TESTING_LOCAL_VOICE_ONLY = False` ก่อนเช็คผลเทสจริงจัง**

## ⚠️ สิ่งที่ต้องทำก่อนใช้งานจริงต่อ (ยังไม่ได้ทำ)

1. **Revert `TESTING_LOCAL_VOICE_ONLY = False`** (บรรทัด ~29 `friday_walkie_talkie.py`) — คุณภาพเสียง local ไม่พอเป็นเสียงหลัก ตามผลทดสอบข้อ 7a
2. **ทดสอบซ้ำ "เปิด Notepad" ด้วยเสียงจริง (edge-tts) หลัง revert** เพื่อยืนยันบั๊ก CONFIRM_WORDS แก้จริงในสถานการณ์ใช้งานจริง (ตอนนี้ยืนยันแค่ด้วย unit test สังเคราะห์ ยังไม่ได้ลองพูดจริงอีกรอบ)
3. รัน `test_tools.py` อีกรอบหลัง revert เพื่อดู 48/48 เต็ม

## ค้างจากก่อนหน้า (ยังไม่เปลี่ยนสถานะ)

- ตอบ Hermes เรื่อง contract 3 ข้อสำหรับ `dispatch_to_hermes` — รอ CEO ยืนยันเนื้อหา
- Test 2 (set_timer stress escalation) — รอ CEO ยืนยัน ceiling
- Wake word / voiceprint แท้ๆ — พักไว้ตามข้อ 3 (ถ้า CEO เปลี่ยนใจอยากได้ speaker auth จริงในอนาคต)
- V6 (rate limiting) — **CEO สั่งตัดออกจาก scope แล้ว ไม่ต้องทำ**
- Phase 3 (VAD/interruptible), Phase 4 (full offline รวมถึง local TTS คุณภาพดีกว่านี้), Telegram integration — ยังไม่เริ่ม

## ลงชื่อ

Commander (Claude) — session 2026-07-02
