# Friday STT Benchmark Dataset

Phase 2 compares providers on the **same real owner speech**, not vendor demo audio.

## Local-only folders

- `benchmarks/stt/audio/` — WAV recordings, do not commit
- `benchmarks/stt/results/` — generated JSONL/summary, do not commit by default
- `benchmarks/stt/manifest.jsonl` — local labeled manifest; start from `manifest.example.jsonl`

## Recording target

Minimum 30 utterances:

- 6 normal Thai conversation
- 6 Thai + English/code-switch terms
- 8 smart-home commands
- 4 numbers/time/temperature commands
- 3 fast/natural speech samples
- 3 normal-room-noise samples

Record the same utterance only once, then run every provider against the exact same WAV file.
Preferred input: mono WAV; the benchmark runner uses SpeechRecognition to load it and the Typhoon adapter normalizes to 16 kHz/16-bit.

## Manifest fields

Each JSONL row requires:

- `id`
- `audio` — relative to this directory or absolute path
- `expected` — reference transcript
- `category`
- `required_terms` — optional command-critical words; all must survive transcription for `command_pass=true`

Example:

```json
{"id":"home-001","audio":"audio/home-001.wav","expected":"เปิดทีวีให้หน่อย","category":"home_command","required_terms":["เปิด","ทีวี"]}
```

## Run

```bash
python src/benchmark_stt.py --manifest benchmarks/stt/manifest.jsonl --providers google,typhoon
```

Google can run on the current Windows Friday machine. Typhoon must first pass optional runtime installation/smoke validation; upstream does not officially support Windows as of 2026-08-26.

## Decision metrics

Use at least:

- exact normalized transcript accuracy
- character error rate (CER)
- command-critical accuracy
- median latency
- p95 latency
- provider error count

Do not switch Friday's production default from Google based only on vendor throughput claims.
