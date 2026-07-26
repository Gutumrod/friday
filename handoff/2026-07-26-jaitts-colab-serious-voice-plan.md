---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-26-jaitts-colab-serious-voice-plan.md
วันที่: 2026-07-26
ผู้เขียน: Codex
---

# Handoff - JaiTTS Colab review and serious Friday voice plan

## สรุปสั้น

CEO ส่งลิงก์ Colab:

`https://colab.research.google.com/drive/16AkcFUGo1mq6DxlJGRhxLcvKzv8SY1LN`

ดึงไฟล์จริงได้เป็น `JaiTTS_F5TTS_Colab.ipynb` ขนาดประมาณ 2.48 MB อัปเดตล่าสุดจาก Drive response `2026-07-26 08:50:10 UTC`.

ข้อสรุป: Colab นี้เกี่ยวกับ Friday โดยตรงในมุม TTS/voice cloning แต่ไม่ควรนำ Colab มาเป็น runtime dependency ของ Friday. ควรใช้เป็น reference workflow เพื่อทำ benchmark local JaiTTS ให้จริงจังขึ้น.

## Source Of Truth ที่เช็คแล้ว

- `AGENTS.md`
- `docs/VOICE_LATENCY_ROADMAP_2026-07-19.md`
- `docs/LIVE_UPGRADE_PLAN_2026-07-03.md`
- `handoff/2026-07-19-voice-latency-phrase-bank-and-ungated-tool-wire.md`
- external Colab notebook downloaded to temp only:
  `C:\Users\Win10\AppData\Local\Temp\JaiTTS_F5TTS_Colab.ipynb`
- public references:
  - `https://huggingface.co/JTS-AI/JaiTTS-F5TTS`
  - `https://github.com/biodatlab/thonburian-tts`
  - `https://arxiv.org/abs/2604.27607`

## Repo / Git State

- repo: `D:\AI-Workspace\projects\friday`
- branch: `master`
- remote: `origin https://github.com/Gutumrod/friday.git`
- `git fetch --all --prune` completed on 2026-07-26 before planning changes.
- pre-existing untracked runtime/output folder observed: `tts_output/`
- Do not touch or commit `tts_output/` unless CEO explicitly asks.

## What the Colab Actually Does

- checks GPU with `nvidia-smi`
- clones `https://github.com/biodatlab/thonburian-tts.git`
- installs repo `requirements.txt`, `ffmpeg`, and `python-crfsuite`
- asks user to upload reference audio and set exact `reference_text`
- optionally uses `google.generativeai` with `gemini-2.5-flash` to split Thai text into natural chunks
- loads:
  - `FlowTTSPipeline`
  - `ModelConfig(language="th", model_type="F5")`
  - `checkpoint="hf://JTS-AI/JaiTTS-F5TTS/model.pt"`
  - `vocab_file="hf://JTS-AI/JaiTTS-F5TTS/vocab.txt"`
  - `vocoder="vocos"`
- sets:
  - `silence_threshold=-45`
  - `cfg_strength=2.0`
  - `nfe_step=32`
  - `speed=1.0`
  - `pipeline.model.remove_silence = True`
- generates per-chunk `.wav` files and stitches them with 150 ms gaps.

## Roadmap Update Made

Edited:

- `docs/VOICE_LATENCY_ROADMAP_2026-07-19.md`

Changes:

- refreshed roadmap status to mention 2026-07-26 JaiTTS-F5TTS Colab evidence
- added the Colab as external JaiTTS reference under Current Spec
- added new `Phase 1.5: JaiTTS Serious Voice Quality Program`
- linked Phase 3 sentence chunking policy to Phase 1.5 findings
- added 2026-07-26 change-log entry

## New Phase 1.5 Intent

ทำ benchmark เสียง Friday แบบจริงจังด้วย local runtime ก่อนเปลี่ยน architecture:

- use Friday env:
  `C:\Users\Win10\miniconda3\envs\friday\python.exe`
- use local models:
  - `D:\models\JaiTTS-F5TTS\model.pt`
  - `D:\models\JaiTTS-F5TTS\vocab.txt`
- evaluate real Friday text:
  startup, confirm prompts, tool replies, Thai-English app names, numbers, date/time, TV/YouTube, Hermes/agent-dispatch wording
- compare:
  - raw full text
  - deterministic local chunking
  - optional Gemini-assisted chunking as benchmark-only
  - current fallback/override path (`edge-tts`)
- test multiple reference-audio variants:
  clean mono 24 kHz 8-12 seconds with exact transcription, longer clip, noisy clip
- keep generated audio out of git and retain only compact report unless CEO asks to keep samples.

## Important Constraints

- Do not run Friday from Colab.
- Do not add Gemini chunking to normal Friday runtime yet.
- Do not replace phrase-bank behavior before benchmark evidence shows quality and latency improvement.
- Do not call local JaiTTS production-ready for long Thai-English technical content without listening benchmark.
- Keep safety/confirm-gate untouched in this planning step.

## Recommended Next Work

1. Build a local benchmark script/report runner, probably under `audit/`, not app runtime.
2. Use 30+ real Friday utterances.
3. Generate temporary audio samples for CEO listening review.
4. Delete temporary audio after review unless explicitly preserving examples.
5. Save compact report with commands/env/CUDA status/results.
6. Only after report passes, decide whether to change runtime chunking or reference policy.

## Verification

Docs-only change. No Python tests run.

