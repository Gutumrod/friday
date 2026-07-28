# Friday Hermes Shadow Targeted Tests Handoff

วันที่: 2026-07-28
branch: `codex/hermes-shadow-targeted-tests`

## What Changed

- `src/friday/hermes_client.py`
  - direct script execution from repo root now finds the `friday` package
  - token redaction is tighter for query tokens and Bearer tokens
- `src/test_tools.py`
  - optional positional filters now run only matching checks
  - no-arg behavior remains the original full suite
- `src/test_hermes_shadow.py`
  - dedicated non-live Hermes shadow safety gate
  - covers exact shadow mode, fire-and-forget scheduling, daemon thread contract,
    metadata-only shadow logs, and token/Bearer redaction
- `docs/FRIDAY_TESTING.md`
  - documents stable non-live gate, targeted gates, live/effectful checks, and Hermes probe
- `audit/HERMES_PHASE0_RUNTIME_CHECK_2026-07-28.md`
  - records verification and runtime probe results
- `audit/hermes_phase0_probe_2026-07-28-runtime.json`
  - machine-local probe evidence from dashboard-down state

## Commands That Passed

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\hermes_client.py src\friday\core.py src\friday\config.py src\test_api.py src\test_tools.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_hermes_shadow.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py non_live
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py hermes_shadow
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py dispatch_to_hermes notify_hermes
C:\Users\Win10\miniconda3\envs\friday\python.exe src\friday\hermes_client.py --probe --write-audit audit\hermes_phase0_probe_2026-07-28-runtime.json
```

## Stop Line Still Active

No implementation was done for:

- `sync` mode
- Hermes live speech
- Hermes `tool_intent`
- Friday executing Hermes-sourced tools
- Confirm Gate changes
- Hermes filesystem/git writes
- Kanban task creation
- Second Brain project reporter

## Next Step

If continuing without owner voice:

- split or label live tests in `src/test_tools.py` so CI/local checks can run a stable non-live subset

If owner voice becomes available:

- run `FRIDAY_FOR_HERMES_MODE=shadow`
- capture 5-10 spoken turns
- inspect `vault/hermes_shadow/YYYY-MM-DD.jsonl` and `vault/latency/YYYY-MM-DD.jsonl`
