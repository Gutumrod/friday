# Friday Voice Cue + Edge TTS Latency Fix

วันที่: 2026-07-28
branch: `codex/hermes-shadow-targeted-tests`

## Context

CEO live-tested Friday and reported two high-priority UX issues:

- ไม่รู้ว่าต้องพูดตอนไหน
- Friday ตอบช้ามาก

## Diagnosis

- `listen_mic()` had only one short start beep before the mic opened. It did not give a second audible state after capturing audio, so the user could not tell whether Friday heard the command and started thinking.
- Live test earlier today showed repeated JaiTTS failures before Edge fallback. Because `speak()` tried JaiTTS first for normal replies, each uncached reply paid the failed-local-TTS cost before speaking.
- Startup also warmed JaiTTS even though the practical fast path now needs Edge TTS first.

## Changes

- `.env.example`
  - added `FRIDAY_TTS_PRIMARY=edge`
- `src/friday/config.py`
  - added `TTS_PRIMARY`, default `edge`
- `src/friday/core.py`
  - default normal `speak()` path now uses Edge TTS first
  - JaiTTS remains available with `FRIDAY_TTS_PRIMARY=jaitts`
  - Edge failure falls back to JaiTTS instead of going silent
  - startup warms JaiTTS only when `TTS_PRIMARY == "jaitts"`
  - `speak_phrase()` no longer tries to generate missing phrase audio through JaiTTS first; it falls back to `speak()`
  - added two cue tones:
    - high short beep before listening starts
    - lower short beep after audio is captured, before STT/LLM thinking
  - cache keys now include the active TTS engine, preventing Edge audio from being reused
    if an operator later switches to JaiTTS
- `src/test_tools.py`
  - added `speak_edge_primary_skips_jaitts` regression
  - kept JaiTTS-primary fallback/cache tests by forcing `fw.TTS_PRIMARY = "jaitts"` inside those tests

## Verification

Passed:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\config.py src\friday\core.py src\test_tools.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py speak_edge_primary_skips_jaitts speak_falls_back_to_edge_tts tts_cache_hit ask_ollama_slow_warning mic_listening_default
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py non_live
```

Results:

- targeted subset: 4/4 passed
- non-live suite: 55/55 passed

Follow-up verification after the cache-key change:

- `speak_edge_primary_skips_jaitts`: passed
- `tts_cache_hit_skips_regeneration`: passed

## Still Open

- Needs CEO live voice test to confirm the two cue tones are understandable in real use.
- `dispatch_to_hermes` can still block for minutes during real calls; fix separately with async/progress UX.
- Confirm behavior remains conservative: `ครับ` alone does not confirm a pending side-effect tool.
