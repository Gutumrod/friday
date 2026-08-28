# Phase 1 — STT Provider Abstraction Evidence

Date: 2026-08-26
Branch: `feat/phase1-stt-provider-abstraction`
Base: `feat/phase0-security-cleanup`
Status: **CODE COMPLETE — LOCAL/LIVE GATE PENDING**

## Implemented

- Added normalized STT provider contract and `STTResult`.
- Added Google provider preserving current behavior:
  - Google Cloud STT when credentials are configured.
  - free `recognize_google` fallback on Cloud request/service failure.
  - no fallback on `UnknownValueError` because that is unclear speech, not service failure.
- Added optional Typhoon file adapter using 16 kHz WAV conversion.
- Added provider factory selected by `FRIDAY_STT_PROVIDER`.
- Production walkie-talkie launcher installs the selected provider before `core.main()`.
- Legacy `core._recognize_speech()` remains untouched as rollback until live verification passes.
- Added provider-specific structured latency metadata.
- Added `.env.example` provider configuration.
- Added `src/test_phase1_stt_provider.py` with seven no-device regression checks.

## Deliberate Limit

Typhoon adapter in this phase is **not streaming**. It converts the captured `AudioData` to a temporary WAV and calls the package transcription API. True microphone chunk streaming is Phase 3 and is blocked until Phase 2 real-speech benchmark evidence exists.

## Typhoon Platform Constraint

As checked on 2026-08-26, the upstream `scb-10x/typhoon-asr` project documents Linux/Mac support and says Windows is not officially supported yet. Friday's current live runtime is Windows-only, therefore:

- `typhoon-asr` is NOT added to base `requirements.txt`.
- Google remains the default production provider.
- Typhoon must be installed/tested separately on a target machine before selection.

## Required Local Gate

When a Friday machine is online:

1. Pull this branch after Phase 0 branch is available locally.
2. Run `python src/test_phase0_security.py`.
3. Run `python src/test_phase1_stt_provider.py`.
4. Run the non-live subset/full `src/test_tools.py` as environment permits.
5. Start Friday with `FRIDAY_STT_PROVIDER=google` and verify 10 spoken turns.
6. Confirm latency log rows include `stt_provider_result` with provider metadata.
7. Do not select Typhoon on Windows until its optional runtime installs and a smoke transcription succeeds.

## Gate

Do not mark Phase 1 PASS or remove the legacy recognizer until the Windows Google parity run passes.
