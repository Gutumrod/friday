# Hermes Phase 0 Runtime Check

วันที่: 2026-07-28
branch: `codex/hermes-shadow-targeted-tests`

## Scope

ตรวจงานที่ทำต่อได้โดยไม่ต้องใช้เสียงจริงของ owner และไม่ใช้ `agy`:

- direct CLI probe ของ `src/friday/hermes_client.py`
- Hermes shadow safety tests แบบ targeted/non-live
- mocked mailbox tests สำหรับ `dispatch_to_hermes` และ `notify_hermes`
- API smoke tests

## Findings

- Fixed direct script execution for `src/friday/hermes_client.py`.
  Before the fix, running from repo root failed with `ModuleNotFoundError: No module named 'friday'`.
- Fixed Hermes error redaction:
  - `?token=...` redaction no longer consumes the rest of the error string.
  - `Bearer ...` redaction now replaces the actual bearer token instead of leaving it behind.
- Added optional filter args to `src/test_tools.py`.
  With no args it keeps the old full-suite behavior. With args it runs matching checks only,
  e.g. `src\test_tools.py hermes_shadow`.
- Added dedicated targeted gate `src/test_hermes_shadow.py` for non-live Hermes shadow checks.

## Runtime Probe

Command:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe src\friday\hermes_client.py --probe --write-audit audit\hermes_phase0_probe_2026-07-28-runtime.json
```

Result:

- command executed successfully
- dashboard at `http://127.0.0.1:9119` was not reachable on this machine at check time
- probe failed gracefully and wrote:
  - `audit/hermes_phase0_probe_2026-07-28-runtime.json`

## Verification

Passed:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\hermes_client.py src\friday\core.py src\friday\config.py src\test_api.py src\test_tools.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_hermes_shadow.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py hermes_shadow
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py dispatch_to_hermes notify_hermes
```

Counts:

- `src/test_api.py`: 2/2 passed
- `src/test_hermes_shadow.py`: 7/7 passed
- `src/test_tools.py hermes_shadow`: 4/4 passed
- `src/test_tools.py dispatch_to_hermes notify_hermes`: 5/5 passed

Not run as a success gate:

- full `src/test_tools.py`, because prior evidence shows it can hang on live JaiTTS/F5-TTS dependency work
- `src/test_tools.py generate_speech_fallback`; it was started accidentally, then the specific test process was stopped before completion because it hits the live JaiTTS path
- real spoken shadow-mode baseline; this still needs owner voice turns

## Current Decision

This is safe to treat as a Phase 0 hardening checkpoint, not a move into sync mode.

Next no-owner task candidate:

- keep improving non-live test isolation around known live checks
- add a documented list of live vs non-live checks if the full suite keeps being too noisy
