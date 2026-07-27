# JaiTTS tts_output Evidence Report

วันที่: 2026-07-27
source folder removed after report: `D:\AI-Workspace\projects\friday\tts_output`

## Summary

`tts_output/` was an untracked runtime/output folder from a JaiTTS experiment dated 2026-07-20. It contained generated `.wav` samples, small scripts, captions, and CapCut alignment metadata for a Body Suit product script.

This report preserves the benchmark evidence needed for future Friday/JaiTTS planning without keeping generated audio artifacts in git.

## Provenance

Observed source files before cleanup:

- `gen_jaitts.py`
- `run_jaitts.bat`
- `script_bodysuit.md`
- `script_bodysuit_v2.md`
- `0720_captions.srt`
- `clips_0720.json`
- `cues_0720.json`
- `aligned_0720.json`
- generated `.wav` files

The generator script used:

- engine: `f5_tts.api.F5TTS`
- model: `F5TTS_v1_Base`
- repo/checkpoint source: `JTS-AI/JaiTTS-F5TTS`
- device: `cuda`
- `nfe_step`: `8`
- output directory: `D:\AI-Workspace\projects\friday\tts_output`
- reference audio: `D:\AI-Workspace\projects\friday\voices\jaitts_reference.wav`
- reference text: Friday voice-cloning greeting/test text

## Script Content

Product:

- Body Suit / บอดี้สูทสายเดี่ยว
- fabric: เรย่อนเกรด A
- sizing: free size, อก 32-40, ส่วนสูง 150-170 cm

Primary generated line set from `script_bodysuit.md`:

| # | Text |
|---:|---|
| 1 | บอดี้สูทตัวเดียว แมทช์ได้หลายลุคจริงไหม |
| 2 | ตัวนี้เป็นผ้าเรย่อน เกรด เอ |
| 3 | ยืดตามตัว ใส่แล้วไม่อึดอัด |
| 4 | จะใส่กับยีน กระโปรง |
| 5 | หรือกางเกงผ้า ก็ดูเข้ารูป |
| 6 | หรือกางเกงผ้า ก็ดูเข้ารูป |
| 7 | สูงประมาณ ร้อยห้าสิบ |
| 8 | ถึงร้อยเจ็ดสิบ ใครชอบลุคเรียบ ๆ |
| 9 | แต่ดูเป๊ะ ตัวนี้น่าลอง |
| 10 | เข้าไปดูสินค้าได้นะ แล้วมาใส่อวดหน่อย |
| 11 | ฟรีไซส์ อก สามสอง ถึง สี่สิบ |

`script_bodysuit_v2.md` also contained a revised 9-line marketing script. `cues_0720.json` indicates an edited caption sequence of 8 cues totaling about 31.4 seconds.

## WAV Metadata

Measured with `ffprobe` before deletion:

| File | Bytes | Duration seconds |
|---|---:|---:|
| `line_01.wav` | 170028 | 3.540 |
| `line_02.wav` | 113708 | 2.370 |
| `line_03.wav` | 112172 | 2.340 |
| `line_04.wav` | 80940 | 1.690 |
| `line_05.wav` | 107564 | 2.240 |
| `line_06.wav` | 107564 | 2.240 |
| `line_07.wav` | 85548 | 1.780 |
| `line_08.wav` | 131116 | 2.730 |
| `line_09.wav` | 94252 | 1.960 |
| `line_10.wav` | 160812 | 3.350 |
| `line_11.wav` | 112172 | 2.340 |
| `test_cuda.wav` | 571436 | 11.900 |
| `test.wav` | 571436 | 11.900 |

Generated line clips total about 26.58 seconds. Test clips total about 23.80 seconds.

## CapCut / Caption Evidence

`clips_0720.json` referenced local CapCut draft media under:

`C:/Users/Win10/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/0720/ai_material/`

`cues_0720.json` contained 8 caption cues:

| # | Start sec | End sec | Text |
|---:|---:|---:|---|
| 1 | 0.0 | 3.9 | สายเดี่ยวสายเล็ก ตัวเดียวจบ ครบทุกลุค |
| 2 | 3.9 | 8.4 | ผ้าเรย่อนเกรดเอ ยืดหยุ่นสูง ใส่แล้วสบาย |
| 3 | 8.4 | 12.2 | เป้าแป๊กแกะได้ สบายใจทุกการเคลื่อนไหว |
| 4 | 12.2 | 15.7 | แมทช์กับยีนส์ก็ร็อค ใส่กับกระโปรงก็หวาน |
| 5 | 15.7 | 18.5 | หรือกางเกงขาสั้น ก็ปังไม่น้อย |
| 6 | 18.5 | 25.1 | ฟรีไซส์ อกสามสอง ถึงสี่สิบ สูงร้อยห้าสิบ ถึงร้อยเจ็ดสิบ ใส่ได้ทุกคน |
| 7 | 25.1 | 28.3 | งานรัดรูปสวย เซ็กซี่แบบมีระดับ |
| 8 | 28.3 | 31.4 | สาว ๆ คนไหนสนใจ คลิกลิงก์เลยจ้า |

`aligned_0720.json` included word-level timing entries, but many later entries were `null`, so the alignment result was partial.

## Benchmark Value

Useful evidence:

- JaiTTS CUDA generation worked on this machine for short Thai marketing lines.
- Short phrase durations were generally 1.69-3.54 seconds.
- The experiment used a low `nfe_step=8`, useful as a speed/quality tradeoff data point.
- The output was connected to a CapCut caption/alignment workflow, but alignment was incomplete.

Limitations:

- This report preserves file metadata and source text only; it is not a new listening-quality verdict.
- Generated audio files were intentionally removed after creating this report.
- The script is product-content oriented, not Friday command/assistant dialogue.

## Cleanup

After this report was created, the generated source folder `tts_output/` was removed from the working tree to avoid committing runtime artifacts and audio samples.

