# Friday for Hermes Phase 0 Review

วันที่: 2026-07-27
ผู้รีวิว: Codex
repo: `D:\AI-Workspace\projects\friday`
branch: `master`

## Scope Reviewed

- อ่าน source of truth:
  - `handoff/2026-07-27-friday-hermes-phase0-shadow-foundation.md`
  - `audit/HERMES_PHASE0_PROBE_2026-07-27.md`
  - `docs/FRIDAY_FOR_HERMES_BUILD_PLAN_2026-07-27.md`
  - `AGENTS.md`
- ตรวจ `git status`, `git diff`, ไฟล์ใหม่ untracked, และ targeted runtime checks
- ไม่แก้ implementation, ไม่ commit, ไม่ push

## Findings

- ไม่พบ blocker ใน Hermes Phase 0 + shadow foundation diff
- default mode ยังเป็น `off`; targeted check ได้ `mode=off` และ `maybe_shadow_hermes_user_text()` คืน `None` โดยไม่ schedule Hermes
- Hermes shadow เรียกหลัง log user text เท่านั้น และเป็น fire-and-forget thread; ไม่มีการนำ Hermes response ไป `speak()` หรือ execute tool
- shadow log ตัด `response_text` ออก เหลือแค่ `response_text_length`; targeted redaction case ไม่หลุด token จาก `token=` / `Bearer`
- `CONFIRM_GATED` ไม่ถูกแก้ใน diff; targeted check เห็น `notify_hermes` ยัง gated และ confirm gate count ปัจจุบัน 21
- audit JSON scan เจอเฉพาะ path `/auth/password-login` จาก OpenAPI manifest ไม่ใช่ secret value; ไม่พบ raw token/Bearer/session-token leak ใน audit artifact จาก pattern scan

## Verification Run

- `git fetch --all --prune`: ผ่าน
- `git status --short --branch`: `master...origin/master [ahead 1]`, มี local implementation diff + untracked Phase 0 artifacts
- `py_compile`: ผ่านสำหรับ `src/friday/core.py`, `src/friday/config.py`, `src/friday/hermes_client.py`
- `src/test_api.py`: ผ่าน 2/2
- `git diff --check`: ผ่าน มีเฉพาะ warning ว่า Git จะ normalize LF -> CRLF ใน 3 tracked files
- `src/test_tools.py`: ไม่จบใน 5 นาที; หยุดเฉพาะ process ที่เริ่มเอง PID 34792
  - stage จาก unbuffered log: ค้างที่ live JaiTTS/F5-TTS generation หลัง `Download Vocos from huggingface charactr/vocos-mel-24khz`, `Converting audio...`, `Generating audio in 1 batches...`
  - ก่อนค้างมี live dependency noise: Ollama API 500 x3 และ Google Cloud STT quota exceeded fallback
  - ยังไม่ได้สรุปว่า test suite fail จาก diff; สถานะคือ live dependency unstable/hanging

## Ready For Owner Approval

พร้อมให้ owner review เพื่อ approve commit/push หลังเลือกว่าจะยอมรับ `test_tools.py` full-suite ที่ยังค้างบน live JaiTTS dependency หรือจะ rerun ตอน dependency stable ก่อน commit

## Next Safest Step

รัน `src/test_tools.py` ซ้ำตอน live JaiTTS/HF dependency stable หรือแยก targeted non-live Hermes/security tests เป็น gate เพิ่ม แล้วค่อยขอ owner approval เพื่อ commit/push Phase 0 + shadow foundation
