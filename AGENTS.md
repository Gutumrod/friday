# AGENTS.md — Friday voice assistant

Read the latest file in `handoff/` (sorted by date in the filename) before doing anything —
it's the actual source of truth for current state, more current than this file or `docs/`.

## What this is

Turn-based Thai voice assistant ("Friday"). Loop: mic → Google STT → Ollama cloud
(`gemma4:31b-cloud`, native tool-calling) → edge-tts (cloud voice) → speaker. Single-file
app: `src/friday_walkie_talkie.py`. Meant to grow into a voice front-door that dispatches
work to other agents (Hermes/OpenClaw) via a shared mailbox — not built yet
(`dispatch_to_hermes`, see handoffs).

## Run / test

```
conda activate friday   # dedicated env, python 3.10 — don't reuse other envs on this machine
python src/friday_walkie_talkie.py   # run from repo root, not from inside src/
python src/test_tools.py             # 51/51 as of 2026-07-02
```

## Platform: Windows only, not ported

This code calls Windows APIs directly and will not run as-is on macOS/Linux:
- `media_control`, `empty_recycle_bin` — `ctypes.windll.*`
- `clipboard_read`/`clipboard_write` — PowerShell `-EncodedCommand`
- `set_timer`'s process-kill-resilient backup — Windows Task Scheduler (`schtasks`,
  `Register-ScheduledTask`, see `_schedule_reminder_task()` / `src/fire_reminder.py`)

If porting to another OS, these four are the actual work — everything else
(SpeechRecognition, edge-tts, pythaitts, pygame, psutil) is already cross-platform.

## Confirm-gate is a hard rule, not optional

Any new tool with a real-world side effect (file changes, app control, anything not
purely read-only) **must** be added to `CONFIRM_GATED` in `friday_walkie_talkie.py` —
this is a standing design decision (see 2026-07-02 handoffs), not something to skip for
convenience. Pure read-only tools (`get_time`, `disk_space`, `system_status`,
`network_status`, `list_processes`) are the only ones left ungated on purpose.

`CONFIRM_WORDS` matching strips trailing Thai politeness particles (ครับ/ค่ะ/ฯลฯ) before
comparing — don't replace this with a blanket prefix-match, it false-positives on unrelated
words (see the `confirm_particle_stripping` test and its handoff for why).

## Machine-local, not in git

`.gitignore` excludes `vault/` (personal facts + conversation history — copy manually
between machines if memory continuity matters), `voices/` (pythaitts auto-downloads its
model on first fallback-TTS use), `backups/` (superseded by git history), `src/tts_cache/`.
None of these are needed to run or test — the app creates/downloads them on first use.

## Docs, in order of trust

1. `handoff/*.md` — dated session logs, most current, read the latest first
2. `audit/FRIDAY_AUDIT.md` — original security audit; many items already fixed since
   (e.g. clipboard_read gating, voice-injection guard) — **verify against current code
   before assuming an item is still open**, don't just trust the checkbox
3. `docs/PRD.md`, `docs/PROJECT_CONTEXT.md` — written early by a different agent, **stale**
   (still describes an earlier architecture), don't trust over handoffs

## Git workflow

Push every checkpoint (commit + push as work lands, not batched at session end) — CEO
works from more than one machine now and pulls from GitHub to stay in sync:
https://github.com/Gutumrod/friday (public repo).

## Style notes from the existing code

- `# ponytail: ...` comments mark deliberate simplifications with a named ceiling — read
  them before "fixing" something that looks incomplete on purpose
- `AUDIO_LOCK` is not reentrant — don't call anything that acquires it from inside code
  that already holds it (this is why the loanword transliteration helper writes its own
  Ollama request instead of reusing `ask_ollama()`)
- Test real `speak()` calls with an isolated `TTS_CACHE_DIR`, or repeated test runs break
  on stale cache from a prior run
