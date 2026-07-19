# Friday Voice Latency Roadmap

วันที่: 2026-07-19
สถานะ: active roadmap, updated after commit 049bc72
เจ้าของงาน: Friday project

เอกสารนี้คือ source of truth สำหรับงานลด latency ของ voice loop ต่อจากนี้ ถ้าย้ายไปทำบน Mac หรือให้ agent อื่นรับช่วง ให้อ่านไฟล์นี้ก่อนเริ่ม และเมื่อทำเฟสไหนจบต้องอัปเดตสถานะในไฟล์นี้ด้วย

## Current Spec

อ้างอิง current project state ณ 2026-07-19:

- repo หลัก: `D:\AI-Workspace\projects\friday`
- branch หลัก: `master`
- voice mode: turn-based / walkie-talkie
- pipeline ปัจจุบัน: microphone -> STT -> LLM/tool routing -> confirm gate -> TTS -> speaker
- launcher เดิม: `src/friday_walkie_talkie.py`
- core implementation: `src/friday/core.py`
- LLM wrapper: `src/friday/llm.py`
- config: `src/friday/config.py`
- UI: `ui/`

ส่วนประกอบสำคัญ:

- STT: Google Cloud Speech-to-Text เป็น path หลัก และ fallback ไป `recognize_google()` เมื่อ Cloud STT ล้มระดับ request
- LLM: Ollama cloud model `gemma4:31b-cloud`
- LLM mode ปัจจุบัน: `stream: false`
- TTS หลัก: JaiTTS local GPU
- TTS fallback / voice override: edge-tts
- safety: tool ที่มี side effect ต้องอยู่ใน `CONFIRM_GATED`
- tests ปัจจุบัน:
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py`
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py`
  - `cd ui && npm run build`

## Goal

ทำให้ Friday โต้ตอบด้วยเสียงไวขึ้นโดยไม่ลดความแม่นของคำสั่ง และไม่ทำให้ confirm gate / safety behavior เสื่อมลง

เป้าหมายเชิงใช้งาน:

- หลังผู้ใช้พูดจบ Friday ต้องเริ่มตอบสนองเร็วขึ้น
- คำสั่งสั้นและ deterministic ต้องไม่ต้องรอ LLM เต็มรอบถ้าไม่จำเป็น
- คำตอบยาวควรเริ่มออกเสียงได้ก่อน LLM สร้างคำตอบครบทั้งก้อน
- tool execution และ confirm gate ต้องยังปลอดภัยเหมือนเดิม
- ถ้าย้ายไป Mac ต้องแยกให้ชัดว่าอะไรเป็น cross-platform และอะไรเป็น Windows-only

## Metrics

ห้ามตัดสินจากความรู้สึกอย่างเดียว ให้ log latency ต่อ turn เป็น structured event

ตัววัดหลัก:

- `listen_latency_ms`: เวลาจากเริ่ม listen จนได้ audio buffer
- `end_of_speech_latency_ms`: เวลาจากผู้ใช้หยุดพูดจริงจน `listen()` return ถ้าวัดได้
- `stt_latency_ms`: audio buffer -> recognized text
- `llm_latency_ms`: recognized text -> LLM response/tool call
- `tool_latency_ms`: tool start -> tool result
- `tts_generation_latency_ms`: text to speak -> audio file ready
- `first_audio_latency_ms`: user speech done -> Friday starts playback
- `total_turn_latency_ms`: user speech done -> Friday finishes speaking
- `cache_hit`: true/false for TTS cache
- `path_type`: `normal_reply`, `tool_call`, `confirm_request`, `confirm_response`, `fast_path`, `error_fallback`

Target รอบแรก:

- simple deterministic command: `first_audio_latency_ms <= 1500`
- normal short command: `first_audio_latency_ms <= 2500`
- long answer: first sentence starts before complete final answer is generated
- no increase in false trigger, missed speech, or confirm-gate bypass
- existing tests still pass

## Phase Plan

### Phase 0: Baseline Instrumentation

Status: in progress

Objective:

- ใส่ profiler ให้ voice loop วัด latency แยกช่วงก่อน optimize
- เก็บ log แบบอ่านข้ามเครื่องได้ เช่น JSONL
- ไม่เปลี่ยน behavior หลัก

Files likely touched:

- `src/friday/core.py`
- optional new helper: `src/friday/latency.py`
- optional log output: runtime-only file under ignored path, not committed

Acceptance criteria:

- มี latency event ต่อ voice turn
- log แยกช่วง listen, STT, LLM, tool, TTS, playback ได้
- test เดิมผ่าน
- มี baseline จากคำสั่งพูดจริงอย่างน้อย 10-20 turn

Implementation notes:

- 2026-07-19: added `src/friday/latency.py` for structured per-turn JSONL logging.
- 2026-07-19: voice loop now records listen, STT, LLM, tool, TTS generation, playback, first-audio, cache-hit, and path type metrics.
- 2026-07-19: latency logs write to `vault/latency/YYYY-MM-DD.jsonl`, which stays runtime-local and ignored by git through `vault/`.
- 2026-07-19: log write is best-effort; a latency logging failure must not crash Friday.
- 2026-07-19: automated validation passed:
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py` -> 73/73 passed
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py` -> 2 tests OK
- 2026-07-19: implementation is complete enough for runtime use, but this phase stays `in progress` because the required 10-20 spoken-turn baseline has not been collected yet.
- 2026-07-19: latest validation after TV preflight work:
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py` -> 76/76 passed
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py` -> 2 tests OK
- Pending before Phase 0 can be marked `done`: run real voice baseline with 10-20 spoken turns and summarize median/p95 bottlenecks here.

Update requirement when done:

- เปลี่ยน status เป็น `done`
- เพิ่มวันที่, commit hash, summary ของค่ากลาง baseline
- ระบุ bottleneck ที่พบจริง

### Phase 1: Low-Risk Latency Wins

Status: in progress

Objective:

- ลด latency โดยไม่แตะ streaming parser หรือ safety gate

Candidate work:

- prewarm JaiTTS ตอน startup หรือก่อน voice loop active
- เพิ่ม/ปรับ TTS cache สำหรับประโยคระบบที่พูดซ้ำ
- เพิ่ม phrase bank สำหรับ startup/status/ack/wait/confirm prompt suffix ที่เจนเสียงเก็บไว้ล่วงหน้า
- fast-path สำหรับคำสั่ง deterministic ที่ปลอดภัย เช่น time/status/read-only tools
- ลด context ที่ส่งเข้า LLM ใน turn ที่ไม่ต้องใช้ history ยาว
- เพิ่ม UI/API status event: listening, transcribing, thinking, speaking

Acceptance criteria:

- simple deterministic command เข้า target `first_audio_latency_ms <= 1500` หรือดีขึ้นชัดเจนจาก baseline
- ไม่มี regression ใน confirm-gate
- test เดิมผ่าน

Implementation notes:

- 2026-07-19: changed JaiTTS startup warmup from blocking-before-greeting to background-after-greeting, after live testing showed Friday felt stuck before saying the first "สวัสดี".
- 2026-07-19: moved microphone ambient-noise calibration to after the audible greeting, while still before the first listen turn, to reduce time-to-first-voice.
- 2026-07-19: planned phrase bank categories for pre-generated JaiTTS audio:
  - `greeting`: short startup identity lines.
  - `ready`: explicit signal that microphone is now ready.
  - `ack`: safe acknowledgement that does not imply the action has completed.
  - `wait_short`: short waiting/status lines for slow operations.
  - `working`: neutral work-in-progress lines.
  - `confirm_suffix`: short confirmation endings such as "ยืนยันไหมคะนาย", "ตกลงใช่ไหมคะนาย", "คอนเฟิร์มไหมคะนาย".
- 2026-07-19: `confirm_suffix` phrases are safety-sensitive. They must only be used after the full action-specific confirmation question has already named the action/target, never as a standalone prompt.
- 2026-07-19: phrase bank manifest should include at least `phrase_id`, `category`, `text`, `file`, `safe_before_action`, and `requires_action_context`.
- 2026-07-19: implemented phrase bank in `src/friday/phrases.py` and runtime phrase audio directory `src/tts_cache/phrases/`.
- 2026-07-19: startup now uses phrase audio for:
  - `greeting_hello_short`: "สวัสดีค่ะนาย"
  - `startup_checking_mic_voice`: "ขอเช็คไมค์กับวอร์มเสียงแป๊บนึงค่ะ"
  - `ready_listening`: "พร้อมฟังค่ะนาย"
- 2026-07-19: generated 21 JaiTTS phrase `.wav` files locally under `src/tts_cache/phrases/`. These are runtime cache files and should not be committed.
- 2026-07-19: promoted 8 selected historical JaiTTS `.wav` files from `src/tts_cache/tts_cache.rar` into named runtime phrase files for greeting, ready, signoff, close clarification, and TV error flows. See `docs/TTS_CACHE_RAR_SELECTION_2026-07-19.md`.
- 2026-07-19: listed current ungated tools from code: `close_camera`, `disk_space`, `get_time`, `list_processes`, `list_timers`, `look_camera`, `network_status`, `system_status`.
- 2026-07-19: wired progress phrases only for safe ungated tool paths. Initial wiring is `look_camera` -> `working_looking`; fast read-only tools intentionally stay silent to avoid adding latency.
- 2026-07-19: if moving to Mac or a fresh checkout, regenerate phrase audio by importing Friday in the right env and running `ensure_all_phrase_audio()`.
- 2026-07-19: automated validation passed after this change:
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\core.py src\friday\latency.py src\test_tools.py`
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py` -> 74/74 passed
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py` -> 2 tests OK
- 2026-07-19: startup choreography was live-tested successfully after commit `b5e87dc`:
  - Friday speaks `สวัสดีค่ะนาย`
  - then `ขอเช็คไมค์กับวอร์มเสียงแป๊บนึงค่ะ`
  - then calibrates mic while quiet
  - then speaks `พร้อมฟังค่ะนาย`
  - then starts listening and warms JaiTTS in the background
- 2026-07-19: TV connection error flow now uses vetted phrase-bank text and fails fast before entering `pywebostv` when the configured TV IP is offline or stale. Commit: `049bc72`.
- 2026-07-19: current low-risk wins are implemented, but this phase stays `in progress` until Phase 0 has before/after spoken metrics.

Update requirement when done:

- เปลี่ยน status เป็น `done`
- บันทึกว่า optimization ไหนทำจริง
- ใส่ before/after metric จาก Phase 0

### Phase 2: Immediate Acknowledgement

Status: not started

Objective:

- ให้ Friday แสดงหรือพูด acknowledgement เร็วขึ้นสำหรับงานที่ต้องรอนาน

Candidate work:

- แยก short ack ออกจาก final answer
- ใช้ cached audio สำหรับ ack เช่น "รับทราบค่ะ กำลังเช็คให้"
- จำกัด ack ไม่ให้พูดทับ confirm prompt หรือทำให้ผู้ใช้เข้าใจว่า action สำเร็จแล้วทั้งที่ยังไม่สำเร็จ
- tool ที่นานควรมี status update แต่ยังรักษา single source of truth ของ result

Acceptance criteria:

- long-running command มี response signal เร็วขึ้น
- ack ไม่ทำให้ safety semantics เพี้ยน
- error path ยังบอกผลจริง ไม่หลอกว่าสำเร็จ

Current recommendation:

- Start this only after the UI/API end-to-end verification pass, because UI events can provide a non-audio acknowledgement channel for slow commands without adding spoken latency.
- First candidate tools: `search_web`, `dispatch_to_hermes`, `tv_play_video`, and `look_camera` only if live logs show they still feel slow.
- Keep fast read-only tools silent unless metrics show a real user-facing wait.

Update requirement when done:

- เปลี่ยน status เป็น `done`
- บันทึก ack rules และข้อห้าม
- เพิ่มตัวอย่าง log 3-5 turn

### Phase 3: Streaming LLM + Sentence TTS

Status: not started

Objective:

- ให้คำตอบยาวเริ่มพูดตั้งแต่ประโยคแรก แทนการรอ LLM response ครบก้อน

Constraints:

- ห้าม execute partial tool call
- ถ้า response เป็น tool call หรือ confirm-sensitive path ให้ใช้ non-streaming path เดิมก่อน
- streaming ใช้เฉพาะ final natural-language reply ที่ปลอดภัย
- ต้องมี parser ที่แยก sentence boundary ได้พอสำหรับภาษาไทย/อังกฤษปนกัน

Files likely touched:

- `src/friday/llm.py`
- `src/friday/core.py`
- tests around tool call handling and confirm-gate behavior

Acceptance criteria:

- long answer starts playback before full response completes
- no tool-call regression
- no confirm-gate bypass
- test เดิมผ่าน และมี test ใหม่สำหรับ streaming fallback

Update requirement when done:

- เปลี่ยน status เป็น `done`
- บันทึก streaming policy ที่ใช้จริง
- บันทึก cases ที่ยัง fallback เป็น non-streaming

### Phase 4: Better Turn-Taking / VAD

Status: not started

Objective:

- ทำให้ระบบรู้ว่าผู้ใช้พูดจบเร็วและแม่นกว่าใช้ `pause_threshold` อย่างเดียว

Candidate work:

- ทดลอง VAD/end-of-speech detector
- เก็บ false-cut และ missed-speech rate จากเสียงจริง
- เพิ่ม interrupt เฉพาะคำปลอดภัยก่อน เช่น "หยุด", "ยกเลิก", "พอ"

Acceptance criteria:

- ลด `end_of_speech_latency_ms`
- ไม่เพิ่มการตัดกลางคำ
- ไม่เพิ่ม false trigger จากเสียงลำโพงหรือเสียงรอบข้าง

Update requirement when done:

- เปลี่ยน status เป็น `done`
- บันทึก VAD config และผลทดสอบปากจริง
- ระบุ rollback path

### Phase 5: Live / Full-Duplex Decision

Status: deferred

Objective:

- ตัดสินใจว่าจะย้ายไป Live/full-duplex architecture หรือไม่ หลังมีตัวเลขจาก Phase 0-4

Decision gate:

- ทำ Phase 0-4 แล้วยังไม่ถึง target
- ผู้ใช้ต้องการพูดแทรกระดับคำจริง ไม่ใช่ turn-based ที่เร็วขึ้น
- มี design ใหม่สำหรับ tool confirmation และ safety แล้ว
- โมเดล Live candidate ผ่าน prompt-injection และ tool-safety test จริง

Current decision:

- ยังไม่เริ่ม
- ยังไม่ควรย้าย architecture เพียงเพื่อแก้ความรู้สึกช้า

Update requirement when decision changes:

- เปลี่ยน status จาก `deferred` เป็น `accepted` หรือ `rejected`
- บันทึกเหตุผล, model/provider, safety test, expected migration cost

## Mac Handoff Notes

ถ้ายกไปทำบน Mac:

- ห้าม assume ว่า Windows-only tools ใช้ได้ เช่น Task Scheduler, PowerShell clipboard, ctypes Windows APIs
- แยก latency work ที่เป็น cross-platform ก่อน เช่น instrumentation, LLM streaming, TTS cache policy
- ตรวจ dependency ของ JaiTTS/F5-TTS บน Mac ใหม่ทั้งหมด โดยเฉพาะ GPU/MPS/CPU fallback
- อย่า commit local voice assets, model cache, generated audio, runtime logs
- ถ้าไม่มี Google Cloud credential path เดิม ให้ใช้ environment/config ที่ชัดเจน ไม่ hard-code path จาก Windows
- ก่อนแก้ code บน Mac ให้อ่าน `AGENTS.md`, handoff ล่าสุด, และไฟล์นี้ก่อน

## Update Protocol

ทุกครั้งที่ทำงานเกี่ยวกับ voice latency:

1. อ่านไฟล์นี้ก่อนเริ่ม
2. อัปเดต status ของ phase ที่ทำ
3. เพิ่มวันที่, commit hash ถ้ามี, และ summary สั้นๆ
4. ใส่ before/after metrics ถ้ามี
5. ถ้าเกิด rollback หรือ decision เปลี่ยน ให้บันทึกไว้ใน phase นั้น
6. ถ้างานเปลี่ยน current spec ให้แก้ `Current Spec` ด้วย

ใช้ status เหล่านี้เท่านั้น:

- `not started`
- `in progress`
- `done`
- `blocked`
- `deferred`
- `rejected`

## Change Log

- 2026-07-19: created roadmap from current Friday repo state and new latency planning discussion.
- 2026-07-19: Phase 0 started. Implementing structured latency logging for the current voice loop before behavior changes.
- 2026-07-19: Phase 0 instrumentation implemented and automated tests passed. Status remains `in progress` until real spoken baseline is collected.
- 2026-07-19: Phase 1 started from live startup feedback. JaiTTS prewarm now runs in the background after the audible greeting.
- 2026-07-19: Startup follow-up found process creation to first listen still around 10s; greeting cache exists, so calibration was moved after greeting to improve time-to-first-voice.
- 2026-07-19: Added phrase-bank design notes, including confirm-gate suffix phrases and their safety constraints.
- 2026-07-19: Implemented fixed phrase bank and seeded 21 local JaiTTS phrase audio files. Friday is still not opened after this change per user instruction.
- 2026-07-19: Promoted 8 vetted phrase variants from `tts_cache.rar` into named phrase IDs without opening Friday.
- 2026-07-19: Wired phrase progress only for ungated `look_camera`; gated tools remain untouched.
- 2026-07-19: Live-tested startup phrase choreography successfully and added TV connection preflight/error phrase wiring in commit `049bc72`.
- 2026-07-19: Roadmap status refreshed. Phase 0 and Phase 1 remain `in progress` only because spoken baseline metrics are still pending, not because implementation is missing.
