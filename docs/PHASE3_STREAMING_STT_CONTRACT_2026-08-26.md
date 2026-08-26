# Phase 3 — Streaming STT Contract

Date: 2026-08-26
Branch: `feat/phase3-streaming-stt-contract`
Parent: `feat/phase2-stt-benchmark-harness`
Status: **CONTRACT READY — PRODUCTION WIRING BLOCKED BY PHASE 2**

## Why This Branch Exists

Friday's current microphone loop is stable turn-based capture. Do not replace it before real benchmark evidence exists.

This branch prepares a model-agnostic streaming contract and state machine only. It does not open the microphone, load NeMo, or change `core.listen_mic()`.

## Current Candidate Update

As checked 2026-08-26, Typhoon now publishes `typhoon-ai/typhoon-asr-streaming-115m`, a cache-aware streaming FastConformer-Transducer model. Its model card describes chunked encoder-cache streaming and points to a NeMo streaming loop. This is more appropriate for a true Phase 3 implementation than forcing the earlier full-context Real-Time model into pseudo-streaming.

The candidate still requires runtime/platform validation. Do not add it to Friday's base Windows dependencies yet.

## Implemented

- `StreamingSTTEngine` protocol
- `StreamingTranscript` partial/final event type
- `StreamingAudioPolicy`
- deterministic PCM chunk sizing
- mono/sample-width validation
- maximum utterance duration guard
- `StreamingSTTSession` lifecycle:
  - reset/start
  - push PCM chunks
  - finish
  - reject invalid lifecycle operations
- fake-engine tests with no microphone/model dependency

## Stop Line

Do not wire this into the production voice loop until Phase 2 evidence decides:

- model/provider
- target OS/runtime
- accuracy requirement
- chunk/latency target
- Thai-English code-switch tolerance

Production migration must preserve a config rollback to the legacy turn-based capture path.
