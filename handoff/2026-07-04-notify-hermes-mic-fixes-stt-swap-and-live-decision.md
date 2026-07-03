---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-04-notify-hermes-mic-fixes-stt-swap-and-live-decision.md
วันที่: 2026-07-04 (เซสชันเริ่มเย็น 2026-07-03 ต่อเนื่องข้ามคืน)
ผู้เขียน: Commander (Claude)
---

# Handoff — notify_hermes เสร็จ, mic/STT fix 2 จุด (รอทดสอบ), ตัดสินใจพักเรื่อง Live

ต่อจาก [2026-07-03-a1-verify-closed-dispatch-bugs-found.md](2026-07-03-a1-verify-closed-dispatch-bugs-found.md)
และ [docs/N8N_MAILBOX_NOTIFIER_2026-07-03.md](../docs/N8N_MAILBOX_NOTIFIER_2026-07-03.md)

## สรุปสั้น

1. **`notify_hermes` tool ใหม่ — เสร็จ, เทสแล้ว, commit+push แล้ว** (`8fac26c`)
2. **mic/STT fix 2 จุด — เขียนแล้ว, unit test ผ่านหมด, แต่ยังไม่ได้ทดสอบปากจริง** (ค้างไว้พรุ่งนี้เช้า, ยังไม่ commit)
3. **JaiTTS — เจอ local Thai TTS candidate ที่มีแวว หลัง demo แล้ว CEO ว่า "ดีกว่าแบบฟ้ากับเหว" เทียบ VachanaTTS/Fish Audio — ยังไม่ integrate จริง** (ดูหัวข้อท้ายสุด)
3. **ตัดสินใจ: พักเรื่อง Gemini Live ไว้ก่อน** — ไม่ใช่ตัดทิ้ง แค่ยังไม่ถึงเวลา (ดูหัวข้อท้ายสุด)

---

## 1. `notify_hermes` — fire-and-forget mailbox tool (commit `8fac26c`, pushed)

ช่องว่างที่ [N8N_MAILBOX_NOTIFIER_2026-07-03.md](../docs/N8N_MAILBOX_NOTIFIER_2026-07-03.md) ทิ้งไว้
("ฝั่งรับ n8n→Telegram เสร็จแล้ว แต่ Friday ยังไม่มีโค้ดเขียนไฟล์เข้า inbox") — ปิดแล้ว

- `tool_notify_hermes(args)` ใน `friday_walkie_talkie.py` — เขียนไฟล์ลง `mailbox/inbox/hermes/`
  ตรงๆ ไม่ block ไม่รอผล (ต่างจาก `tool_dispatch_to_hermes` เดิมที่ยังเก็บไว้คู่กัน สำหรับงานที่ต้องรอผลจริง)
  CONFIRM_GATED เหมือนเครื่องมืออื่นที่มีผลจริง
- **Live-tested end-to-end จริง 3 รอบ:** สั่งด้วยเสียงธรรมชาติ ("บอก Hermes...ไม่ต้องรอตอบกลับนะ")
  → Friday (gemma4) เลือก `notify_hermes` ถูกต้อง (ไม่ใช่ `dispatch_to_hermes`) → ยืนยัน → ไฟล์เข้า
  inbox จริง → n8n poll เจอ → Telegram แจ้งเตือนจริง
- **เจอบั๊กจริงระหว่างทาง: n8n ส่ง Telegram ด้วย Markdown parse_mode โดยไม่ escape** — `_` ในชื่อไฟล์
  หายหมดตอนแสดงผล (ยืนยัน 2/2 ครั้ง) แก้ฝั่ง Friday แล้ว (เปลี่ยนตัวคั่นชื่อไฟล์เป็น `-` + sanitize
  อักขระ Markdown พิเศษ `_`/`*`/`` ` ``/`[`/`]`) ทดสอบซ้ำแล้วผ่าน แต่ **ต้นเหตุจริงยังอยู่ฝั่ง n8n**
  (ถ้าข้อความที่ผู้ใช้พูดเองมีอักขระพวกนี้ปนมา ก็ยังเสี่ยงหายอยู่ดี) — บันทึกไว้ให้ Hermes แก้ต่อใน
  `docs/N8N_MAILBOX_NOTIFIER_2026-07-03.md` ("อัปเดต 2026-07-03 เย็น")
- อัปเดต `build_system_prompt()` ด้วย (เคยบอกโมเดลว่า "ส่ง Telegram ไม่ได้" — stale แล้ว)

69/69 → 69/69 (test suite ตอนนั้น)

---

## 2. Gemini brain-swap — ลองแล้วถอยกลับ (ไม่มีผลกระทบ, ไม่เคย commit)

CEO อยากให้ Friday "โต้ตอบไวกว่านี้" → ลองสลับ `ask_ollama()` จาก gemma4 ไป Gemini
(`gemini-2.5-flash` ผ่าน OpenAI-compat endpoint) เจอ 2 เรื่องระหว่างทาง:

- ต้องเปิด `reasoning_effort: "none"` เพราะ thinking mode ทำให้บาง tool-call ได้ completion_tokens=0
- **เจอ security regression จริง:** payload injection เดิม (2026-07-02, `[TOOL: empty_recycle_bin()]`
  ปนในผลค้นหา) ที่ gemma4 เคยต้านได้ 100% — Gemini พูดตามคำโกหกซ้ำ **ทุก reasoning_effort level**
  ไม่ใช่แค่ reasoning_effort=none

จากนั้น CEO เอง**สรุปว่าหลงทาง** — ปัญหาจริงไม่ใช่ตัวโมเดล แต่เป็นจังหวะ mic/STT (ดูข้อ 3 ด้านล่าง)
โค้ดทั้งหมดยังไม่เคย commit เลย ถอนด้วย `git checkout --` กลับไป commit ล่าสุดทันที ไม่มีอะไรเสีย
`.env` ที่มี Gemini API key (จ่ายเงินจริง ไม่ใช่ free tier — CEO ตั้งใจเลือกแบบนี้ "ไม่อยากไปแย่งใครใช้")
ยังอยู่บนดิสก์เฉยๆ เผื่อกลับมาใช้วันหลัง

---

## 3. mic/STT fix 2 จุด — เขียนเสร็จ, **ยังไม่ทดสอบปากจริง**, ยังไม่ commit

จากหลักฐานจริง (transcript session-03 ที่ CEO เอามาให้ดู: ตัดกลางคำ "F..." ก่อนจะพูด "Friday" จบ)
สรุปว่า**ไม่ใช่** `pause_threshold` (ตัดหลังเงียบไปพักหนึ่ง) แต่เป็น 2 จุดนี้:

### 3a. `dynamic_energy_threshold` → ปิด (`friday_walkie_talkie.py`, `main()`)
เดิมเปิดไว้ (`True`) ทำให้ threshold ปรับตัวต่อเนื่องทุกเทิร์น เสียงแทรกสั้นๆ (ลำโพงสะท้อน/แอร์) ดัน
threshold ขึ้นได้ ทำให้พยางค์แรกที่เบากว่าโดนตีความเป็นความเงียบ — ปิดหลัง `adjust_for_ambient_noise()`
ครั้งแรก ให้ค่านิ่งไม่ขยับ

### 3b. STT: `recognize_google()` (ฟรี ไม่เป็นทางการ) → `recognize_google_cloud()` (ทางการ)
CEO ถามว่า STT เดิมเสียเงินไหม/มีดีกว่าไหม → เช็คแล้วพบว่าเป็น endpoint ฟรีไม่เป็นทางการ (อธิบาย
บั๊ก "ยันต์" ที่เจอมาได้) เทียบตัวเลือกแล้วเลือก **Google Cloud Speech-to-Text** (ทางการ, multilingual
โดยธรรมชาติ, เปลี่ยนโค้ดน้อยสุด) **ตัดตัวเลือก Thonburian Whisper ออก** เพราะ fine-tune จาก Thai-only
dataset เสี่ยง catastrophic forgetting กับ code-switching (ชื่อแอปภาษาอังกฤษปนไทยที่ Friday เจอเป็นประจำ)
— ยืนยันด้วย research จริง ไม่ใช่เดา

- Credentials: ยืม service account ของ `craftbike_bot` (`D:\craftbike_bot\credentials.json`,
  project `craftbikebot`) — CEO ยืนยันว่า project นี้ว่างไม่ได้ใช้อะไร ใช้ร่วมได้ ต้องเปิด
  Speech-to-Text API เองผ่าน GCP Console ก่อน (service account เปิด API เองไม่ได้ ลองแล้วโดน
  PERMISSION_DENIED) — เปิดแล้ว, ทดสอบยิงจริงสำเร็จ
- เพิ่ม fallback: ถ้า Cloud STT ล้มเหลวแบบ request-level (`sr.RequestError` — เงิน/quota/API ปิด/
  service account โดนถอน) จะ fallback ไปที่ `recognize_google()` ฟรีตัวเดิมอัตโนมัติ ไม่ใช่เงียบไปเลย
  (ไม่ fallback ตอน `UnknownValueError` เพราะฟังไม่ชัดจะฟังไม่ชัดเหมือนกันทั้งคู่)
- Refactor: ดึง transcription logic ออกมาเป็น `_recognize_speech(r, audio)` แยกจาก `listen_mic()`
  ทำให้เทสได้เป็นครั้งแรก (เดิม `listen_mic()` เทสไม่ได้เลยเพราะต้องมีไมค์จริง)
- เพิ่ม `google-cloud-speech` ใน `requirements.txt`
- 73/73 tests ผ่าน (4 ใหม่ครอบคลุม fallback)
- **Live-simulated 6-turn conversation** (สังเคราะห์เสียงด้วย VachanaTTS แล้วยิงผ่าน STT+LLM+TTS จริง
  เพื่อสร้าง usage จริงให้ CEO เช็คบิล) — ผลลัพธ์ 4/6 ถูกต้อง, 1/6 ฟังผิด ("ซีพียู"→"ที่อยู่", คนละ
  แบบกับบั๊ก "ยันต์" เดิม แต่ยืนยันว่า Cloud STT ก็ไม่สมบูรณ์แบบ), 2/6 ฟังไม่ออกเลย (แต่เสียงสังเคราะห์
  คุณภาพต่ำ ไม่ใช่ตัวแทนเสียงคนจริง) — **นี่ไม่ใช่บทพิสูจน์สุดท้าย ต้องรอทดสอบปากจริง**

**ค้างไว้พรุ่งนี้เช้า:** CEO จะทดสอบพูดจริงผ่านไมค์ ทั้ง 3a+3b รวมกัน ถ้าโอเคค่อย commit
(ถ้าไม่โอเคต้องแยกดูว่าตัวไหนเป็นสาเหตุ) — rollback ไม่มีต้นทุน: `git checkout -- src/friday_walkie_talkie.py requirements.txt`
กลับไป `8fac26c` ทันที

---

## ตัดสินใจ: พัก Gemini Live ไว้ก่อน (ไม่ใช่ตัดทิ้ง)

Gemini (ตัวช่วยอื่น ไม่ใช่ Commander) เสนอ `gemini-3.1-flash-live-preview` มาให้ CEO ดู — เช็คแล้วข้อมูล
ถูกต้องจริง (โมเดลมีจริง ใหม่กว่าที่เคย research ไว้เมื่อวาน, ราคา $3/$12 ต่อ 1M audio token ตรงกับที่หาเจอ)
แต่ CEO ชี้ประเด็นสำคัญ: บั๊กทุกตัวที่ไล่แก้คืนนี้เป็นเรื่องจังหวะ mic/STT ไม่มีอันไหนเป็นเรื่อง "อยากพูด
แทรกกลางประโยค" เลย — **สรุปคงสถาปัตยกรรม turn-based (walkie-talkie) ไว้** เพราะเครื่องมือ 29 ตัวที่มี
ใช้ได้หมดทันที ไม่ต้องรื้อ CONFIRM_GATED ใหม่ ต้นทุน/ความเสี่ยงต่ำกว่า Live migration มาก

**เงื่อนไขกลับมาคุยใหม่ (CEO's own words):** "จนกว่าจะอยากได้แบบนั่งเถียงกันระดับคำพูด ไม่ใช่ประโยค
ต่อประโยค" — คือต้องการ barge-in ระดับคำจริงๆ ไม่ใช่แค่เร็วขึ้น ถึงจะกลับมาพิจารณา Live

**ข้อควรระวังถ้ากลับมาคุยเรื่องนี้วันหลัง:** ช่องโหว่ prompt-injection ที่เจอใน `gemini-2.5-flash`
(หัวข้อ 2 ข้างบน) ไม่เคยทดสอบกับ `gemini-3.1-flash-live-preview` เลย — คนละโมเดล คนละสถาปัตยกรรม
ห้ามสรุปว่าช่องโหว่เดียวกันโดยไม่ทดสอบซ้ำ

---

## JaiTTS — local Thai TTS candidate ที่มีแวว (ยังไม่ integrate จริง)

CEO ได้คำแนะนำจาก AI อื่น 2 เจ้าไปเช็คให้:

- **Gemini แนะนำ ChatTTS — ผิด, ตัดทิ้ง.** เช็ค GitHub ตัวจริงแล้วรองรับแค่จีน+อังกฤษ ไม่มี training
  data ไทยเลย ข้ออ้าง "คอมมูนิตี้ไทยเจอ seed พูดไทยชัด" ไม่จริงในทางเทคนิค (seed แค่เลือกน้ำเสียงจาก
  ที่โมเดลรู้จักอยู่แล้ว ไม่ได้ปลดล็อกภาษาใหม่ที่ไม่เคยเทรน)
- **Grok แนะนำ JaiTTS-v1.0 — ของจริง เช็คแล้วน่าเชื่อถือ.** paper จริงบน arXiv (`2604.27607`),
  repo จริง (`JTS-AI-Team/JaiTTS`), **ออกแบบมาเพื่อ Thai-English code-switching โดยตรง** (ตัวเลข/
  ศัพท์อังกฤษไม่ต้อง normalize พิเศษ) CER 1.94% ต่ำกว่า human baseline 1.98% ในงานสั้นๆ ตรงกับที่
  หาเจอเป๊ะ (Grok แนะนำ Kokoro-82M กับ XTTS-v2 มาด้วยแต่ผิด — สองตัวนั้นไม่รองรับไทยเลยสักตัว
  เช็คจาก HF/doc ตรงแล้ว)

**Integration จริงไม่ง่าย (เช็คก่อนแนะนำให้ CEO ลงทุนเวลาต่อ):** repo GitHub เป็นแค่ eval harness
(`cal_wer.sh`/`cal_sim.sh`, requirements.txt เป็นของ Chinese-NLP ecosystem) ไม่ใช่ inference code
ใช้งานจริง โค้ดตัวอย่างใน HF model card (`JTS-AI/JaiTTS-F5TTS`) เรียก package ชื่อ `flowtts` ซึ่ง
**ไม่มีอยู่จริงบน PyPI** ทางที่ใช้ได้จริงคือต่อ checkpoint (`model.pt`+`vocab.txt`, based on F5-TTS
+ custom XLM-R duration predictor) เข้ากับ `f5-tts` package จริง (มีอยู่จริง แต่ต้องเขียน glue code
เอง ไม่ใช่งาน 10 นาที) — ไม่ได้เริ่มลง GPU ติดตั้งอะไรคืนนี้ กลัวซ้ำรอย WSL2/Fish Audio CUDA OOM
ที่เคยพังทั้งระบบมาก่อน

**CEO ลองผ่าน demo เว็บแทน** (`jaitts-demo.jts.co.th`, zero-shot voice cloning ต้องการ reference
audio ≥8 วิ + transcript คู่กัน) Commander สร้าง reference clip จากเสียง Premwadee (edge-tts) ที่
ใช้อยู่แล้วให้ (รอบแรกแค่ 7.3 วิ demo ปฏิเสธ ต้องสร้างใหม่ยาว ~9.7 วิ) **จงใจไม่ใช้เสียง Friday จาก
หนัง Iron Man ตามที่ CEO ขอตอนแรก** — เสียง Kerry Condon จากหนังมีลิขสิทธิ์ Disney/Marvel เอามา
clone พูดประโยคใหม่ที่นางไม่เคยพูดจริงมีความเสี่ยงทั้งลิขสิทธิ์และสิทธิ์ส่วนบุคคล ปฏิเสธไปตรงๆ
CEO เปลี่ยนไปใช้เสียงที่สร้างจาก Google AI Studio เป็น reference แทนในที่สุด

**ผล: CEO's own words — "ดีกว่าแบบฟ้ากับเหว" เทียบ VachanaTTS/Fish Audio S2 Pro** ครั้งแรกที่มี
local Thai TTS candidate ที่ฟังดูใช้ได้จริง หลัง 2 ตัวก่อนหน้าพังทั้งคู่

---

## JaiTTS integration จริง — เสร็จ, commit `051ed83`, pushed

CEO บอก "ต่อเลย ยังมีเวลาอยู่" ให้ integrate เข้า production คืนนั้นเลย:

- เช็คสเปกเครื่องก่อน: RTX 2080 Ti 11GB (ว่าง ~9.4GB), RAM 31.8GB (ว่าง 11.8GB), disk เหลือ 107GB
  — **ต่อ GPU แบบ native บน Windows โดยตรง ไม่ผ่าน WSL** (เลี่ยงบั๊ก WSL2/Fish Audio CUDA OOM เดิม)
- ลง `torch==2.6.0+cu124` + `torchaudio` + `f5-tts` (v1.1.20) จริง — พบว่า `f5_tts.api.F5TTS` มี
  Python API ใช้งานได้ตรงๆ (`ckpt_file=`/`vocab_file=` รับ checkpoint กำหนดเองได้) ไม่ต้องพึ่ง
  `flowtts` ที่ไม่มีจริงเลย
- โหลด checkpoint จริงจาก `JTS-AI/JaiTTS-F5TTS` ผ่าน `huggingface_hub`, ทดสอบ inference จริง
  (โหลด 2.9s, gen 2.4s สำหรับเสียง 3.88s) — สำเร็จตั้งแต่รอบแรก
- **แทนที่ `generate_speech_fallback()` (เดิม VachanaTTS) ด้วย JaiTTS ทั้งหมด** ใน
  `friday_walkie_talkie.py` — ลบ `_transliterate_loanwords()`/`_FALLBACK_TTS_SUBSTITUTIONS` ที่
  มีไว้แก้ปัญหาเฉพาะของ VachanaTTS ออกด้วย (ไม่จำเป็นแล้ว เพราะ JaiTTS handle code-switching เอง),
  ลบ `pythaitts` dependency, เพิ่ม `torch`/`torchaudio`/`f5-tts`/`huggingface_hub`
  เก็บ reference voice (จากที่ CEO ทดสอบ demo ด้วย Google AI Studio) ไว้ที่ `voices/jaitts_reference.wav`
- ทดสอบผ่าน `speak()` จริง (ไม่ใช่แค่ function เดี่ยวๆ) ด้วยประโยคที่มี "Chrome"/"YouTube" ปน —
  เล่นเสียงจริงออกลำโพง 67/67 tests ผ่าน

**Commit hygiene bug พบระหว่างแยก commit:** ตอน commit `notify_hermes` (`8fac26c`) เมื่อคืนก่อน
ผม `git add` ทั้งไฟล์แทนที่จะแยกเฉพาะส่วนที่ตั้งใจ ทำให้ `dynamic_energy_threshold=False`
(mic fix ที่ยังไม่เคยทดสอบปากจริง) ติดขึ้น GitHub ไปด้วยโดยไม่ได้ตั้งใจ — แก้ไขด้วยการ revert
ทั้งไฟล์กลับไป base แล้ว re-apply แยกทีละชุดใหม่ (verify ด้วย `diff` ว่าผลลัพธ์สุดท้าย byte-ต่อ-byte
ตรงกับก่อนแยก) จน commit `051ed83` มีแค่ JaiTTS ล้วนๆ ส่วน Google Cloud STT ยังคงไม่ commit ตามเดิม
**บทเรียน: เช็ค `git diff --stat` ก่อน `git add` ไฟล์ที่มีการเปลี่ยนแปลงหลายเรื่องปนกันเสมอ**

---

## JaiTTS ใช้ได้กับ Friday แต่ใช้ไม่ได้กับ content-pipeline

CEO ทดสอบเพิ่มกับสคริปต์โฆษณาจริงจาก content-pipeline
(`คะน้าหมูชิ้น_script_30-06-2026.txt`, 7 บรรทัด) — เจนเสียงแบบเพิ่มบรรทัดทีละ 1 จนครบ 7 บรรทัด
(93 → 532 ตัวอักษร) ผลทางเทคนิคดีมาก (RTF นิ่งที่ ~0.20 ทุกความยาว ไม่มีอาการแย่ลงเมื่อยาวขึ้น)
**แต่ CEO ฟังจริงแล้วเจอออกเสียงผิดทุกรอบ** — "หมูกรอบ" กลายเป็น "หมู" (ตัด "กรอบ" หาย), "กรุบกรอบ"
กลายเป็น "กรุ๊บกรอบ" (วรรณยุกต์ผิด) **สรุปของ CEO: ใช้กับ Friday (ประโยคสั้นๆ) ได้ แต่เอาไปทำ
content video ไม่ได้** — ภาษาโฆษณาไทยที่ซ้ำคำ/เล่นเสียงเยอะ (แบบที่ content-pipeline ใช้จริง)
คือจุดที่มันพัง ซึ่งไม่โผล่ในประโยคสั้นแบบที่ Friday ใช้ **ห้ามเข้าใจผิดว่าผลดีจาก Friday แปลว่าใช้
กับ content-pipeline ได้ด้วย เป็นคนละข้อสรุปกัน**

---

## ถัดไป (สำหรับ session ใหม่)

1. **รอ CEO ทดสอบปากจริง** (mic threshold + Google Cloud STT, ยังไม่ commit) — ถ้าโอเค commit ทันที
   ถ้าไม่โอเคไล่แยกว่าจุดไหนเป็นสาเหตุ
2. `notify_hermes` (commit `8fac26c`) — ยังไม่มีอะไรต้องทำต่อ นอกจากถ้า Hermes แก้ Markdown
   parse_mode ฝั่ง n8n เสร็จแล้ว ควรทดสอบซ้ำว่าอักขระพิเศษอื่นๆ (`*`/`` ` ``) ก็รอดด้วยไหม
3. Gemini Live — พักไว้ตามเงื่อนไขข้างบน ไม่ต้องหยิบขึ้นมาเองถ้า CEO ไม่เอ่ย
4. **JaiTTS สำหรับ content-pipeline** — ถ้า CEO อยากลองต่อ: ต้องหาทางแก้ปัญหาออกเสียงคำซ้ำ/เล่นเสียง
   ผิด (ลอง reference audio อื่น, tune parameter, หรือ post-edit ทีละบรรทัด) ก่อนเชื่อถือได้พอจะใช้
   จริงกับลูกค้า — ยังไม่มีทางแก้ที่ชัดเจน ณ จุดนี้
5. ของค้างเก่าที่ยังไม่แตะ: YouTube profile-picker flakiness (ล็อกไว้ตามเดิมตามคำสั่ง CEO), n8n
   "CBL Product Pipeline v4" OAuth token หมดอายุ (คนละระบบ ไม่เกี่ยว Friday)

## ลงชื่อ

Commander (Claude) — session 2026-07-03 เย็น ถึง 2026-07-04 ดึก (04:20)
