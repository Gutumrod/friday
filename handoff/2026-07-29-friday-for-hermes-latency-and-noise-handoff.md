# Friday for Hermes Latency + Noise Handoff

วันที่: 2026-07-29
branch: `codex/hermes-shadow-targeted-tests`

## Goal Locked By CEO

เป้าหมายหลักห้ามเปลี่ยน:

- ทำ Friday แจกได้ เพื่อให้คนเอาไปเชื่อมกับ Hermes ตามชื่อ **Friday for Hermes**
- คุยต้องลื่น ไม่ให้ผู้ใช้รอเงียบๆ โดยไม่รู้ระบบทำอะไรอยู่
- ต้องช่วยงานได้จริง ไม่ใช่แค่ demo voice assistant

## Current Implementation State

Latest pushed commits:

- `6530492 fix: improve Friday voice response cues`
- `5af374e fix: make Hermes dispatch asynchronous`
- `33eecdc chore: instrument Friday listen end reasons`

สำคัญ:

- Edge TTS เป็นเสียงหลักแล้วผ่าน `FRIDAY_TTS_PRIMARY=edge`
- cache key แยกตาม TTS engine แล้ว เพื่อไม่ให้เสียงเก่าปนกับ Edge
- `dispatch_to_hermes` ไม่บล็อก voice loop แล้ว
- Friday ส่งงานเข้า mailbox แล้วตอบกลับทันทีว่าให้คุยต่อได้
- Friday เก็บ pending Hermes job แบบ bounded เท่านั้น:
  - `task_id`
  - `title`
  - `status`
  - `created_at`
- ผล Hermes จะถูกตรวจจาก mailbox ภายหลังตอน Friday idle
- ถ้า Friday กำลังฟังหรือกำลังพูดอยู่ จะไม่ลบงานออกจาก registry ก่อนแจ้งผล

## Backend Verification Already Done

ไม่ใช้ไมค์ ไม่เปิด Friday live และไม่สร้างงาน Hermes จริง:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\core.py src\test_tools.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py dispatch_to_hermes
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py listen_end_reason latency_turn_writes_jsonl
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py non_live
```

Latest non-live suite result after listen instrumentation:

- `56/56 passed`

## Latency Diagnosis So Far

จาก `vault/latency/2026-07-28.jsonl`:

- worst foreground blocker เดิมคือ `dispatch_to_hermes` รอ Hermes ประมาณ 180 วินาที
- ตอนนี้แก้เป็น async แล้ว
- STT ปกติอยู่ระดับไม่กี่วินาที
- LLM ปกติอยู่ระดับไม่กี่วินาที แต่มี spike ได้
- TTS หลังเปลี่ยน Edge อยู่ระดับไม่กี่วินาทีและ cache ช่วยได้
- listen window หลายรอบแตะ 15 วินาที จึงต้องแยกว่า:
  - ผู้ใช้พูดยาวจริง
  - หรือ background audio ทำให้ระบบไม่เห็นความเงียบ

## New Listen Instrumentation

`src/friday/core.py` เพิ่ม metrics/events เพื่อวิเคราะห์รอบฟังเสียง:

- `listen_started`
  - `timeout_seconds`
  - `phrase_time_limit_seconds`
  - `pause_threshold_seconds`
  - `energy_threshold`
  - `dynamic_energy_threshold`
- `listen_captured`
  - `end_reason`
  - `elapsed_ms`
- metrics:
  - `listen_end_reason`
  - `listen_phrase_time_limit_hit`

ค่าที่ตั้งไว้ตอนนี้:

- `LISTEN_START_TIMEOUT_SECONDS = 10`
- `LISTEN_PHRASE_TIME_LIMIT_SECONDS = 15`
- `LISTEN_PAUSE_THRESHOLD_SECONDS = 0.8`
- `LISTEN_PHRASE_LIMIT_MARGIN_SECONDS = 0.35`

หมายเหตุ: instrumentation นี้ยังไม่เปลี่ยน behavior การฟังจริง แค่ทำให้ log บอกได้ว่าจบรอบฟังเพราะอะไร

## Important New Hypothesis

CEO สังเกตว่าเคสชน 15 วินาทีอาจเกิดจากเปิดทีวีอยู่ ทำให้เสียงทีวีเข้าไมค์ตลอด

ข้อสรุปทางเทคนิค:

- ถ้าเสียงทีวีหรือเสียงฉากหลังเข้าต่อเนื่อง `SpeechRecognition.listen()` อาจไม่เจอช่วงเงียบตาม `pause_threshold`
- เมื่อไม่เห็นความเงียบ ระบบจะรอจนชน `phrase_time_limit = 15`
- ถ้าเป็นแบบนี้ latency ก้อน listen ไม่ได้เกิดจาก STT ช้า แต่เกิดจาก capture ไม่ยอมปิดรอบฟัง

## Next Test Recommendation

ทดสอบเสียงจริงแบบสั้น แต่ยังไม่ควรแก้ threshold ก่อนเห็น log:

1. เทสทีวีปิดหรือเบามาก 5-10 turn
2. เทสทีวีเปิดตามสภาพใช้งานจริง 5-10 turn
3. เทียบสัดส่วน:
   - `listen_end_reason = pause_or_silence`
   - `listen_end_reason = phrase_time_limit`
   - `listen_phrase_time_limit_hit = true`

การแปลผล:

- ถ้า `pause_or_silence` เยอะตอนทีวีปิด แต่ `phrase_time_limit` เยอะตอนทีวีเปิด:
  - root cause คือ background audio / TV bleed
- ถ้า `phrase_time_limit` เยอะทั้งสองเคส:
  - ต้องดู mic gain, energy threshold, noise suppression, หรือ VAD
- ถ้า `pause_or_silence` เยอะทั้งสองเคส:
  - listen ไม่ใช่ปัญหาหลักแล้ว ให้กลับไปดู STT/LLM/TTS/path routing

## Candidate Fixes If TV Bleed Is Confirmed

เรียงจาก conservative สำหรับของแจก:

1. แนะนำใช้ headset mic / directional mic / Windows noise suppression / RTX Voice เป็น setup guidance
2. เพิ่ม runtime warning/log เมื่อ `phrase_time_limit` ชนบ่อย เพื่อบอกว่า environment เสียงดัง
3. เพิ่ม optional noise-profile calibration หรือ VAD เฉพาะเครื่อง
4. ทำ push-to-talk / hold-to-talk fallback สำหรับห้องเสียงดัง
5. เฟสใหญ่กว่า: เปลี่ยนเป็น chunked/streaming audio pipeline แทน `SpeechRecognition.listen()` เดิม

ยังไม่ควรลด `phrase_time_limit` ทื่อๆ เพราะผู้ใช้ต้องพูดยาวได้ และเป้าหมายคือคุยลื่นแบบใช้งานจริง ไม่ใช่ตัดคำเร็วแต่พัง

## Do Not Reopen Unless Asked

- อย่ากลับไปใช้ old voice cache เป็น active path
- อย่า hardcode microphone/speaker device index สำหรับของแจก
- อย่าให้ Hermes output ข้าม confirm gate
- อย่าให้ Friday เก็บ full conversation เพิ่มใน pending job registry
- อย่าเปิด live Friday หรือใช้ไมค์จริงถ้าผู้ใช้ขอ backend-only

## Untracked Files Observed

ยังมี untracked runtime/audit files จากงานก่อนหน้า ไม่เกี่ยวกับ handoff นี้และไม่ควร commit โดยไม่ตั้งใจ:

- `_quarantine_audio_2026-07-28/`
- `audit/hermes-dashboard-9119.err.log`
- `audit/hermes-dashboard-9119.out.log`
- `audit/hermes_phase0_probe_live_now.json`
