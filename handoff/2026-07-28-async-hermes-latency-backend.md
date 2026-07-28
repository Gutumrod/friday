# Friday Async Hermes Latency Backend Handoff

วันที่: 2026-07-28
branch: `codex/hermes-shadow-targeted-tests`

## Context

CEO asked to inspect the whole Friday system for latency reduction opportunities, then clarified
that testing must be backend-only: no real microphone test and no live Friday voice loop.

Latest latency log for 2026-07-28 showed the worst foreground blocker was
`dispatch_to_hermes` waiting on Hermes for about 180 seconds. Other recurring costs were the
current microphone listen windows, STT, LLM, TTS generation, and playback, but those need live
voice validation before tuning thresholds.

## Changes

- `src/friday/core.py`
  - changed `dispatch_to_hermes` from foreground poll/wait to background mailbox dispatch
  - added durable pending Hermes job registry under Friday's local vault
  - added idle-boundary delivery of completed Hermes mailbox results
  - delivery now leaves the job pending if Friday is listening or audio is busy
  - updated tool schema and system prompt so Friday treats Hermes as background work, not an
    immediate completion
  - added listen-end instrumentation so future live runs can tell whether capture ended by
    pause/silence or by hitting the phrase-time limit
- `src/test_tools.py`
  - replaced the old blocking-poll expectation with a backend-only async registry regression
  - test confirms dispatch returns quickly, keeps a pending job, does not deliver while busy,
    then delivers and removes the job when idle
  - added backend-only inference coverage for listen end reasons

## Backend Latency Result

The mocked mailbox-create path returned in about 1 ms in targeted tests. This does not measure
real Hermes runtime speed; it verifies Friday no longer waits for Hermes results in the voice
turn.

## Verification

Passed without using microphone or live Friday:

```powershell
C:\Users\Win10\miniconda3\envs\friday\python.exe -m py_compile src\friday\core.py src\test_tools.py
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py dispatch_to_hermes
C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py non_live
```

Results:

- targeted dispatch tests: 2/2 passed
- non-live suite: 55/55 passed

## Remaining Latency Opportunities

- microphone listen windows currently dominate many turns and need a real voice test before
  lowering `timeout` or `phrase_time_limit`
- STT normally costs a few seconds; provider/local VAD changes need real utterance samples
- LLM normally costs a few seconds but can spike badly; add route-specific fast paths only after
  measuring which common commands still hit the model unnecessarily
- Edge TTS is now the default and caching helps repeated replies; do not reintroduce old voice
  cache into the active path
