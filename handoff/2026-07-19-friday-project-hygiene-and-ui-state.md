---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-19-friday-project-hygiene-and-ui-state.md
วันที่: 2026-07-19
ผู้เขียน: Codex
---

# Handoff — Friday project hygiene + current UI state

## สรุปสั้น

โปรเจกต์ `friday` อยู่บน `master` และ sync กับ `origin/master` แล้ว ณ ตอนตรวจ:

- latest commit: `dcae205` (`feat: wire Friday UI to the real API (Phase 4, items 1-5)`)
- Python test หลักผ่านใน env ที่ถูกต้อง
- UI production build ผ่าน
- เพิ่ม ignore สำหรับ `src/voices/` เพราะเป็น local/runtime voice model asset ไม่ควรเข้า git
- `docs/FRIDAY_UI_IMPLEMENTATION_PLAN.md` เป็นเอกสารแผนของ Friday UI ที่ควร track เป็น project doc ไม่ใช่ runtime junk

## Source of truth ที่ใช้

- `AGENTS.md`
- handoff ล่าสุดเดิม: `handoff/2026-07-04-notify-hermes-mic-fixes-stt-swap-and-live-decision.md`
- current git history: `git log --oneline -5`
- current files in `src/friday`, `ui`, `docs`

## Validation

ใช้ Python env ตรง:

`C:\Users\Win10\miniconda3\envs\friday\python.exe`

ผล:

- `src\test_tools.py`: 72/72 passed
- `src\test_api.py`: 2 tests OK
- `ui`: `npm run build` passed (`tsc && vite build`)

หมายเหตุจาก test:

- Python default ของ shell คือ `C:\Python314\python.exe` และไม่มี dependency เช่น `pygame`; อย่าใช้เป็น env สำหรับ Friday
- `conda` command ไม่อยู่ใน PATH ของ shell นี้; ใช้ Python executable ตรงด้านบนแทน
- Google Cloud STT มีข้อความ quota exceeded ระหว่าง test แต่ test fallback ผ่าน
- Google API warning: Python 3.10 support ใน `google.api_core` จะหมดช่วง 2026-10-04

## Git Hygiene

เพิ่มใน `.gitignore`:

- `src/voices/`

เหตุผล:

- พบ untracked `src/voices/speaker_config.json`
- พบ untracked `src/voices/th_f_1.onnx` ขนาดประมาณ 63MB
- เป็น voice/model runtime asset ไม่ควรเข้า git เช่นเดียวกับ `voices/`, `vault/`, `src/tts_cache/`

ลบ generated cache แล้ว:

- `src/__pycache__`
- `src/friday/__pycache__`

`ui/dist/` ถูก ignore โดย `ui/.gitignore` อยู่แล้ว

## Current Project Shape

- core/API อยู่ที่ `src/friday/`
- launcher เดิมยังอยู่ที่ `src/friday_walkie_talkie.py`
- tests:
  - `src/test_tools.py`
  - `src/test_api.py`
- UI อยู่ที่ `ui/`
- Friday UI plan อยู่ที่ `docs/FRIDAY_UI_IMPLEMENTATION_PLAN.md`

## Next Agent Notes

- อ่านไฟล์นี้ก่อน แล้วค่อยอ่าน handoff เก่า 2026-07-04 เฉพาะส่วน voice/STT/JaiTTS ที่ยังเป็น context สำคัญ
- ห้ามใช้ Python 3.14 default ใน shell สำหรับ test Friday
- ถ้าจะรัน test ใช้:
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_tools.py`
  - `C:\Users\Win10\miniconda3\envs\friday\python.exe src\test_api.py`
- ถ้าจะเช็ค UI ใช้:
  - `cd ui`
  - `npm run build`
- อย่า add `src/voices/`, `voices/`, `vault/`, `src/tts_cache/`, `ui/dist/`, หรือ generated cache

