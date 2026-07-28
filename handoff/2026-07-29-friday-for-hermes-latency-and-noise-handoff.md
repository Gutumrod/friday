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
- `501c400 docs: add Friday latency noise handoff`

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

Status after live test: done.

Friday live test was completed after the main voice call was closed. Friday shut down cleanly
by voice command. No code edits or commits were made during the live test. One intentional
real side effect occurred through Friday's confirm gate: the user confirmed a Google Maps/web
search flow.

Live log inspected:

- `vault/latency/2026-07-29.jsonl`

Phase split based on the user's chat note "ผมเปิดทีวีละ":

- Pre-TV / quiet-ish rows 2-11:
  - 10 turns
  - `phrase_time_limit`: 6
  - `pause_or_silence`: 4
  - average listen latency: about 13.25 seconds
- TV-on rows 12-19:
  - 8 turns
  - `phrase_time_limit`: 8
  - `pause_or_silence`: 0
  - average listen latency: about 15.04 seconds

การแปลผล:

- TV/background audio hypothesis is strongly supported for the TV-on phase: every post-TV
  turn hit `phrase_time_limit`.
- The quiet-ish phase still hit `phrase_time_limit` in 6/10 turns, so the root cause is not
  only TV. Next diagnosis must include mic gain, recognizer energy threshold/noise
  calibration, Windows/RTX noise suppression, VAD, or push-to-talk fallback.
- Friday was conversationally usable and confirm gate worked, but listen capture remains the
  dominant latency source.

## Updated Latency Plan

Priority order for the next session:

1. Diagnose capture/end-of-speech first
   - inspect `energy_threshold` and `dynamic_energy_threshold` from the 2026-07-29 live log
   - compare rows that ended with `pause_or_silence` vs `phrase_time_limit`
   - decide whether the current calibration/threshold is too permissive for the room
2. Add a low-risk environment warning
   - if `listen_phrase_time_limit_hit` repeats in recent turns, log/say a short warning that
     background audio is preventing end-of-speech detection
   - do not speak the warning while mic is active
3. Try conservative mic/noise settings before replacing the pipeline
   - test Windows/RTX noise suppression and headset/directional mic behavior
   - keep device selection based on system default for distribution; do not hardcode device IDs
4. Add optional fallback interaction mode for noisy rooms
   - push-to-talk or hold-to-talk is acceptable as a fallback, not as the default UX
5. Only then evaluate VAD/chunked streaming
   - WebRTC VAD or sounddevice chunk buffer can be tested if SpeechRecognition's
     `pause_threshold` remains unreliable
   - acceptance must include false-cut and missed-speech checks, not only lower latency

Do not reduce `phrase_time_limit` blindly. The user needs to speak long commands, and the
product goal is smooth real use, not fast-but-broken truncation.

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
