# Phase 2 — STT Benchmark Readiness

Date: 2026-08-26
Branch: `feat/phase2-stt-benchmark-harness`
Parent: `feat/phase1-stt-provider-abstraction`
Status: **HARNESS COMPLETE — DATA/RUNTIME GATE PENDING**

## Ready Now

- Shared manifest format for labeled owner speech.
- Local-only audio/results paths protected by `.gitignore`.
- Runner executes the same WAV through selected providers.
- Metrics:
  - normalized exact accuracy
  - character error rate (CER)
  - command-critical required-term accuracy
  - median latency
  - p95 latency
  - provider error count
- Pure regression tests for benchmark metrics.

## Required Real Evidence

At least 30 owner-spoken WAV files across normal Thai, Thai-English code switching, smart-home commands, numbers/temperature, fast speech, and normal room noise.

## Typhoon Constraint

Upstream Typhoon ASR currently documents Linux/Mac support and no official Windows support. Therefore the benchmark must record Typhoon runtime/install outcome explicitly rather than assuming it is usable on the current Windows Friday machine.

## Gate Rule

Do not switch production STT default or start Phase 3 streaming integration until benchmark evidence demonstrates command accuracy at least equal to the Google baseline with a meaningful latency benefit and stable runtime behavior.
