# Friday Testing Guide

วันที่อัปเดต: 2026-07-28

## Default Rule

Use the Friday conda environment, not the machine default Python:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe
```

Run commands from repo root:

```powershell
D:\AI-Workspace\projects\friday
```

## Stable Non-Live Gate

Use this first for normal implementation checks:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\core.py src\friday\config.py src\friday\hermes_client.py src\test_api.py src\test_tools.py src\test_hermes_shadow.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_hermes_shadow.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py non_live
```

Current verified result on 2026-07-28:

- `src/test_api.py`: 2/2 passed
- `src/test_hermes_shadow.py`: 7/7 passed
- `src/test_tools.py non_live`: 55/55 passed

`non_live` means no real app/window opening, clipboard mutation, media keypress,
browser launch, live web search, live Ollama model call, live JaiTTS/F5-TTS generation,
live Google STT, live Task Scheduler registration, real webcam, or real TV connection.

Some mocked checks still print production-style warning text, such as Ollama/STT failure
messages, because they exercise fallback paths with fake objects.

## Targeted Gates

Hermes shadow only:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_hermes_shadow.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py non_live hermes_shadow
```

Hermes mailbox mocks:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py non_live dispatch_to_hermes notify_hermes
```

API smoke:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py
```

## Live / Effectful Checks

Do not run the full suite casually:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py
```

The full suite may touch real or unstable dependencies, including:

- opening or closing local apps
- clipboard read/write
- media keys / volume keys
- browser launch
- live web search and LLM calls
- live JaiTTS/F5-TTS generation
- Task Scheduler registration
- local network probe

If a full run hangs around JaiTTS/F5-TTS, do not treat that as a Friday/Hermes regression
without isolating the live dependency first.

## Hermes Dashboard Probe

Read-only probe:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\friday\hermes_client.py --probe --write-audit audit\hermes_phase0_probe_YYYY-MM-DD-runtime.json
```

If `http://127.0.0.1:9119` is down, the command should still exit cleanly and write a
fail-graceful audit JSON. A dashboard-down result is runtime evidence, not a code failure.
