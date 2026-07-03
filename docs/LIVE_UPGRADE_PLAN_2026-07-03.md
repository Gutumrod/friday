# แผนอัปเกรด Friday → Full-Duplex Voice Assistant (Gemini Live style) — 2026-07-03

**ทำโดย:** Commander (Claude) — สังเคราะห์จากผลวิจัย 4 สาย (codebase audit, docs history, cloud Live APIs, local OSS stack) เก็บข้อมูล ณ 2026-07-03
**ต่อจาก:** [LIVE_MIGRATION_READINESS_2026-07-03.md](LIVE_MIGRATION_READINESS_2026-07-03.md) — เอกสารนั้นบอก "อะไรรอด" เอกสารนี้คือ "แผนงาน + ทางเลือก API" ที่เอกสารนั้นทิ้งไว้
**สถานะ:** แผนเสนอ CEO — ยังไม่เริ่มลงมือ (มี decision ค้าง 3 ข้อ ดูข้อ 7)

---

## 1. 🎯 ข้อสรุปหลัก (TL;DR)

1. **เส้นทางแนะนำ: Gemini Live API** — เป็นเจ้าเดียวที่ได้ครบทุกข้อที่ Friday ต้องการ:
   รองรับภาษาไทยเป็นทางการ (อยู่ใน 97 ภาษาของ Live API, native-audio ~70 ภาษา),
   barge-in/VAD ในตัว, function calling (แบบ async NON_BLOCKING บนรุ่น native audio),
   **รับ video/camera input ได้ตรง** (กล้องที่เพิ่งทำจะกลายเป็น video stream แทน tool call),
   และมี **free tier ผ่าน AI Studio API key = $0 สำหรับ prototype**
2. **เส้นทาง local 100% (Phase 4 เดิม) ยังไปไม่ถึงในปีนี้** — STT/VAD local พร้อมแล้ว (7/10)
   แต่ TTS ไทย local คุณภาพยังต่ำกว่า edge-tts ชัดเจน (4/10) และ speech-to-speech ไทยแบบ
   full-duplex ยังไม่มีของจริง (2/10, มีแค่ Typhoon2-Audio ที่เป็น turn-based)
3. **โค้ดปัจจุบันไม่เสียเปล่า** — tool layer ทั้ง 28 ตัว + vault + timers + TTS cache
   ย้ายไปได้หมด งานจริงคือเขียน IO/orchestration layer ใหม่ + ออกแบบ confirm-gate
   ให้อยู่รอดในโลกที่ไม่มี "รอบ" ชัดเจน
4. สถาปัตยกรรมแนะนำ: **dual-mode** — โหมด Live (Gemini, ต้องเน็ต) เป็นประสบการณ์หลัก
   และเก็บโหมด walkie-talkie เดิมไว้เป็น fallback ตอนเน็ตล่ม/quota หมด ไม่ลบของเดิมทิ้ง

---

## 2. 📊 ผลเปรียบเทียบ API (ข้อมูล ณ ก.ค. 2026 — verify จากเว็บจริง)

| เกณฑ์ | **Gemini Live** ⭐ | OpenAI Realtime | xAI Grok Voice | Nova 2 Sonic | Local OSS |
|---|---|---|---|---|---|
| ภาษาไทย | ✅ ทางการ (97 ภาษา) | ⚠️ ผ่าน Whisper, ไม่อยู่กลุ่มคุณภาพสูง | ⚠️ "100+ ภาษา" ยังไม่ verify ไทยเจาะจง | ❌ ไม่มีไทย (7 ภาษา) | ✅ STT ดี / ⚠️ TTS พอใช้ |
| Barge-in/VAD | ✅ ในตัว (ปิดเป็น manual ได้) | ✅ | ✅ | ✅ | ✅ (Pipecat+Silero) |
| Function calling | ✅ async NON_BLOCKING (2.5 native audio) | ✅ ดีมาก | ✅ | ✅ | ✅ (ผ่าน Ollama) |
| Video/camera input | ✅ 1 fps JPEG | ❌ | ❌ | ❌ | ❌ (ต้อง tool แยกแบบเดิม) |
| Session limit | 15 นาที audio (ต่อได้ด้วย session resumption) | 60 นาที | 30 นาที | - | ไม่จำกัด |
| ค่าใช้จ่าย ~30 ชม./เดือน | **$0 (free tier)** / paid ~$20–45 | ~$90–180+ | ~$90 ($0.05/นาที) | ~$27 (ใช้ไทยไม่ได้) | $0 + ค่าไฟ |
| Python SDK | google-genai (`client.aio.live.connect`) | openai SDK | WebSocket ตรง + Pipecat plugin | AWS experimental | Pipecat v1.4.0 |

- **Model เป้าหมาย:** `gemini-2.5-flash-native-audio-preview-12-2025` (native audio, 128k context, async tool calling) — ตัวเลือกสำรอง `gemini-3.1-flash-live-preview` (half-cascade, tool calling แบบ sequential)
- **Ollama:** ยังไม่มี realtime voice ใดๆ (แค่ feature request #15807 เปิดอยู่) — ไม่ต้องรอ
- ตัดทิ้ง: Nova Sonic (ไม่มีไทย), ElevenLabs (~$144+/เดือน), vocode (โปรเจคตายแล้ว), Moshi (อังกฤษเท่านั้น), Qwen3-Omni (speech I/O ไม่มีไทย), Kokoro (ไม่มีเสียงไทย)

**Fallback อันดับสอง (ถ้าเสียงไทย Gemini ไม่ผ่านหูจริง):** Grok Voice Agent API — $0.05/นาที flat คาดเดาง่าย, TTFA <1 วิ, มี Pipecat plugin แต่ไม่มี free tier ไม่มี video

---

## 3. 🏗️ สถาปัตยกรรมเป้าหมาย (dual-mode)

```
                    ┌──────────────────────────────────────────┐
 ไมค์ ──► audio in ─┤          friday core (async)             │
                    │  Mode A: Gemini Live (WebSocket stream)  │──► ลำโพง (PCM stream)
 กล้อง ─► video ────┤  Mode B: walkie-talkie เดิม (fallback)   │
                    └───────────────┬──────────────────────────┘
                                    │ function calls
                    ┌───────────────▼──────────────────────────┐
                    │  tools/ (ย้ายจาก monolith — 28 tools,     │
                    │  CONFIRM_GATED, vault, timers, Hermes)    │
                    └──────────────────────────────────────────┘
```

หลักการ:
- **แยก capability ออกจาก orchestration ก่อน** (ตาม LIVE_MIGRATION_READINESS) — ได้ประโยชน์ทันทีแม้ยังไม่ทำ Live: monolith 1,567 บรรทัดจะเล็กลง, fire_reminder.py เลิก import pygame ทั้งก้อน
- **Confirm-gate ยังเป็น hard rule** — ในโหมด Live เปลี่ยนจาก state machine แบบรอบ เป็น **pending-tool + spoken confirm**: โมเดลเรียก gated tool → ระบบ hold การ execute แล้วให้ Friday ถามยืนยันด้วยเสียง → คำตอบถัดไปที่ตีความเป็น yes/no ปลด hold (ใช้ NON_BLOCKING function calling ของ Gemini 2.5 native audio ที่รองรับ pattern นี้ตรงๆ)
- **Event bus กลาง** — ทุก state change (idle/listening/thinking/speaking/tool-pending) ยิงเป็น event เดียวกัน ทั้ง core ใช้เอง และ Golden HUD (FRIDAY_UI_DESIGN.md) เสียบ WebSocket ฟังได้เลยในอนาคต

---

## 4. 📋 แผนงานเป็นเฟส

### Phase A — ปิดหนี้ + แยกชั้น (โครงสร้างพร้อมรื้อ) — ~2-4 เซสชัน
| # | งาน | หมายเหตุ |
|---|---|---|
| A1 | **Verify ค้าง:** ทดสอบ full voice pipeline ผ่านไมค์จริง + dispatch_to_hermes end-to-end จริง | ทุก handoff ย้ำว่าเป็นงานค้างใหญ่สุด — ต้องปิดก่อนรื้อ ไม่งั้นแยก regression จากของพังเดิมไม่ออก |
| A2 | แยก `tools.py` (28 tools + TOOLS + TOOL_SCHEMAS + CONFIRM_GATED), `vault.py`, `timers.py`, `tts.py` ออกจาก monolith | ระหว่างแยก แก้หนี้ `_pack_args` — ให้ tool รับ structured kwargs เลิก format `"a|b"` |
| A3 | ย้าย pygame.mixer.init() ออกจาก module import; fire_reminder.py import เฉพาะ tts | ปลด side-effect ตอน import |
| A4 | รัน test_tools.py เป็น regression gate ของ tool layer (ยอมรับว่า loop-level tests จะต้องเขียนใหม่) | 61/61 คือ baseline |

### Phase B — PoC Gemini Live (พิสูจน์เสียงไทย + barge-in) — ~2-3 เซสชัน
| # | งาน | เกณฑ์ผ่าน |
|---|---|---|
| B1 | สคริปต์ PoC เดี่ยว: google-genai SDK + `client.aio.live.connect` + mic in/speaker out (PCM stream) บน AI Studio free tier | คุยไทยโต้ตอบได้, ขัดจังหวะกลางประโยคได้จริง |
| B2 | **ทดสอบคุณภาพเสียงไทย**: อ่านตัวเลข, ชื่อเฉพาะ, code-switching ไทย-อังกฤษ, เลือก voice จาก 30 HD voices | CEO ฟังแล้วรับได้เทียบ PremwadeeNeural |
| B3 | ทดสอบ function calling: ต่อ tool ง่าย 1 ตัว (get_time) + gated 1 ตัว (set_timer) ด้วย pattern pending-tool confirm | confirm ด้วยเสียงทำงานถูกใน stream ต่อเนื่อง |
| B4 | ทดสอบ session resumption + context compression ข้ามกำแพง 15 นาที | คุยต่อเนื่อง >15 นาทีไม่หลุดบริบท |
| **Gate:** ถ้า B2 ไม่ผ่าน (เสียงไทยไม่ไหว) → ทดลอง Grok Voice ($0.05/นาที) ก่อนพิจารณา OpenAI | | |

### Phase C — Migrate ของจริง — ~4-6 เซสชัน
| # | งาน |
|---|---|
| C1 | เขียน async core ใหม่: audio in/out streams + Gemini Live session + event bus (แทน main loop เดิม) |
| C2 | แปลง TOOL_SCHEMAS → Gemini function declarations (เนื้อหา name/description ก็อปได้ ปรับ format), ต่อครบ 28 tools ผ่าน adapter |
| C3 | ย้าย confirm-gate ครบ 18 gated tools ด้วย pending-tool pattern + ทดสอบ bypass cases (บทเรียนจาก confirm-gate-bypass เดิม) |
| C4 | กล้อง: เปลี่ยนจาก tool `look_camera` เป็น video stream เข้า session (จำกัด audio+video session 2 นาที → เปิดกล้องเฉพาะตอนถูกถาม แล้วปิด — ใกล้ pattern snapshot-on-ask เดิม) |
| C5 | Vault/memory: inject facts.md เข้า system instruction, log transcript จาก server-side transcription events |
| C6 | Dual-mode switch: Gemini ล่ม/quota หมด → ตกกลับ walkie-talkie เดิมอัตโนมัติ + แจ้งด้วยเสียงจาวิส |

### Phase D — Hardening + ของแถม — ตามจังหวะ
- dispatch_to_hermes แบบ async (เลิก blocking poll 300s — ในโหมด Live ห้าม block อยู่แล้ว ใช้ NON_BLOCKING tool + แจ้งผลเมื่อเสร็จ)
- Golden HUD เสียบ event bus (ออกแบบไว้แล้วใน FRIDAY_UI_DESIGN.md — สถาปัตยกรรมตรงกันพอดี)
- ประเมิน paid tier ถ้าใช้เกิน free quota (~$20–45/เดือนที่ 1 ชม./วัน)

**ไม่ทำ (ตัดออกชัดเจน):** รอ Ollama realtime (ไม่มี timeline), local speech-to-speech ไทย (ยังไม่มีของจริง — ติดตาม Qwen3.5-Omni weights และ Typhoon audio รุ่นถัดไป), Pipecat เต็มรูป (จำเป็นเมื่อทำ local pipeline — เก็บไว้เป็นแผนสำรองถ้าเลิกใช้ cloud)

---

## 5. ⚠️ ความเสี่ยงหลัก

| ความเสี่ยง | ผลกระทบ | ทางกัน |
|---|---|---|
| Gemini Live ยังเป็น **preview** — model id เปลี่ยน/deprecate บ่อย (รุ่น 09-2025 เพิ่ง deprecate มี.ค. 2026) | โค้ดพังเมื่อ Google หมุนรุ่น | pin model id ใน config เดียว, เก็บ walkie-talkie mode ไว้เสมอ |
| Free tier quota เป็น project-specific ไม่การันตี + มีรายงาน billing trap ตอนเปิด billing | ใช้จริง 1 ชม./วันอาจชน quota | เช็คตัวเลขจริงใน AI Studio ตอน PoC, ทำ quota-exceeded → fallback mode |
| คุณภาพเสียงไทย (ตัวเลข/ทับศัพท์/สำเนียง) ไม่มี benchmark ทางการ | เลือกผิดเจ้าเสียเวลา migrate | B2 คือ gate — CEO ฟังเองก่อน commit Phase C |
| Confirm-gate ใน stream ต่อเนื่องเป็น pattern ใหม่ ไม่มีของเดิมให้ลอก | ช่องโหว่ side-effect tool | ทำใน B3 ก่อนด้วย tool เดียว + ไล่ bypass cases ตอน C3 |
| Session billing ของ Gemini คิด context สะสมซ้ำทุก turn | paid tier แพงกว่าที่คิดถ้าคุยยาว | เปิด context window compression ตั้งแต่แรก |
| edge-tts (โหมด fallback) โดน MS block มาแล้ว 2 รอบ (2024, ม.ค. 2026) | fallback mode เสียงหาย | มี VachanaTTS fallback อยู่แล้ว — คงไว้ |

---

## 6. 💰 ต้นทุนโดยประมาณ (ใช้ ~1 ชม./วัน)

- **Prototype (Phase B):** $0 — AI Studio free tier
- **ใช้จริง:** $0 ถ้าอยู่ใน free quota; ถ้าต้อง paid: Gemini native audio ≈ **$20–45/เดือน** (เทียบ Grok ≈ $90, OpenAI ≈ $90–180+)
- อ้างอิงราคา: https://ai.google.dev/gemini-api/docs/pricing (audio in $3/1M tok, audio out $12/1M tok, 32/25 tok/วินาที)

---

## 7. ❓ Decision ที่ CEO ต้องเคาะก่อนเริ่ม

1. **เห็นชอบเส้นทาง Gemini Live เป็นหลัก + walkie-talkie เป็น fallback?** (แทนที่จะรอ local 100% ตาม Phase 4 เดิม — local TTS/S2S ไทยยังไม่พร้อมจริง)
2. **ยอมรับว่า "สมอง" ของโหมด Live เปลี่ยนจาก gemma4:31b-cloud (Ollama) เป็น Gemini?** — persona/กติกาย้ายผ่าน system instruction ได้ แต่พฤติกรรมโมเดลจะต่างจากเดิม
3. **ลำดับงาน: ปิด verify ค้าง (A1) ก่อนเริ่มรื้อ ใช่ไหม?** — Commander แนะนำว่าใช่

---

## 8. 🔗 แหล่งอ้างอิงหลัก

- Gemini Live API: https://ai.google.dev/gemini-api/docs/live-api/capabilities , https://ai.google.dev/gemini-api/docs/pricing
- OpenAI Realtime: https://developers.openai.com/api/docs/guides/realtime
- Grok Voice Agent: https://x.ai/news/grok-voice-agent-api , https://docs.pipecat.ai/api-reference/server/services/s2s/grok
- Ollama realtime (ยังไม่มี): https://github.com/ollama/ollama/issues/15807
- Pipecat: https://github.com/pipecat-ai/pipecat (v1.4.0, 2026-06-17)
- Thai STT: https://github.com/biodatlab/thonburian-whisper (+ CT2: Vinxscribe/biodatlab-whisper-th-large-v3-faster)
- Thai TTS local: https://github.com/VYNCX/F5-TTS-THAI , https://github.com/VYNCX/VachanaTTS
- Thai S2S: https://github.com/scb-10x/typhoon2-audio/
- edge-tts block history: https://github.com/rany2/edge-tts/issues/458
