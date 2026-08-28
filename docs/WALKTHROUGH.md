# Friday Walkthrough — Current Runtime

**Last Updated:** 2026-08-26

This file describes how to run the current stable Friday baseline on `master`. Feature-branch behavior may require additional environment variables or tests before it is merged.

## Runtime Baseline

Friday currently runs as a Windows-oriented turn-based voice assistant.

```text
Mic
 -> SpeechRecognition capture
 -> Google Cloud STT (`th-TH`)
 -> free Google recognizer fallback on Cloud request failure
 -> Ollama native structured tool calling
 -> Friday tool layer / Confirm Gate
 -> JaiTTS local voice primary
 -> Edge TTS fallback / alternate voice
 -> pygame playback
```

The main implementation lives under `src/friday/`; `src/friday_walkie_talkie.py` is a compatibility launcher that delegates to `friday.core`.

## Requirements

Current expected environment on the original Windows machine:

- Python 3.10 in Conda env `friday`
- dependencies from `requirements.txt`
- working microphone/audio output
- Ollama endpoint expected by current config
- optional Google Cloud STT credential path if using the Cloud recognizer
- local JaiTTS model assets downloaded on first use as required

Do not reuse an unrelated Python environment; the repo has Windows/audio/ML dependencies that can conflict with other projects.

## Run Voice Mode

From the repository root:

```powershell
cd D:\AI-Workspace\projects\friday
C:\Users\Win10\miniconda3\envs\friday\python.exe src\friday_walkie_talkie.py
```

or use:

```powershell
run_friday.bat
```

The launcher must be run from the repository root so relative paths and the local vault behave as expected.

## Run API / UI Backend

Current repo includes a FastAPI service boundary.

```powershell
run_friday_api.bat
```

The service exposes the current API/UI integration layer including chat, tools, confirmation, and event-stream behavior documented in the source.

## Test Commands

Primary regression command from the existing repo workflow:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py
```

Also run API tests where applicable:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py
```

Feature branches added on 2026-08-26 contain additional phase-specific test files. Run those from the branch being reviewed before opening/merging its PR.

## Voice Interaction

At startup Friday:

1. initializes the recognizer
2. speaks a startup greeting/status
3. calibrates ambient microphone noise
4. locks the calibrated energy threshold
5. enters the turn-based listen loop

When the console indicates Friday is listening, speak normally. Current capture is still phrase-based rather than true streaming ASR.

Current hard shutdown phrases include commands such as:

- `จบการทำงาน`
- `ปิดเครื่อง`
- `ลาก่อน`
- `บ๊ายบาย`

## Tool Safety

Friday uses native structured tool calls. The old `[TOOL: ...]` embedded-text parser is obsolete.

Tools with real side effects must pass `CONFIRM_GATED`. Do not add a new side-effect tool without a matching confirmation policy and regression coverage.

Read-only tools are the deliberate exception.

## Machine-Local Files

The following are intentionally not repository state and may need to be recreated/copied when moving machines:

- `.env`
- `vault/`
- local TTS cache/model state
- machine/device credentials

Never commit live credentials or paired device keys.

## Feature-Branch Work Waiting for Validation

Current prepared branches cover:

- security/config cleanup
- STT provider abstraction
- Google vs Typhoon benchmark harness
- streaming STT contract
- Home Assistant read-only client/tools
- logical device registry
- confirm-gated smart-home writes
- legacy AC/IR readiness
- Hermes tool-intent validation
- remote command security contract
- Home Assistant scene orchestration

These are not equivalent to merged production behavior. See `PROJECT_CONTEXT.md` and the latest `handoff/` file before testing or merging.

## When the Windows Machine Comes Back Online

Start with Phase 0, not the newest branch:

1. fetch/pull latest repository refs
2. check out `feat/phase0-security-cleanup`
3. create/fill local `.env` without committing it
4. rotate/re-pair the LG webOS key that was previously exposed in public history
5. run phase security tests + full existing regression
6. perform real TV validation
7. only then proceed through later branch gates

Do not jump directly to smart-home write branches simply because their code has already been prepared.
