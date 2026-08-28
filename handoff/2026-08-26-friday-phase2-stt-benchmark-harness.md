# Friday Phase 2 STT Benchmark Handoff

Date: 2026-08-26
Branch: `feat/phase2-stt-benchmark-harness`
Parent: `feat/phase1-stt-provider-abstraction`
Status: HARNESS READY / REAL AUDIO PENDING

When a machine is available:

1. Copy `benchmarks/stt/manifest.example.jsonl` to ignored `benchmarks/stt/manifest.jsonl`.
2. Record at least 30 owner-spoken WAV files under ignored `benchmarks/stt/audio/`.
3. Run Google first and establish baseline.
4. Install/smoke Typhoon only on a compatible/test machine; record install/runtime failure if unsupported.
5. Run `python src/benchmark_stt.py --manifest benchmarks/stt/manifest.jsonl --providers google,typhoon` when both providers are available.
6. Review generated summary under ignored `benchmarks/stt/results/`.
7. Write a compact evidence report before any production provider switch.

Phase 3 true streaming remains blocked until this evidence exists.
