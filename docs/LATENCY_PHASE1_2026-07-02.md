# Latency Phase 1 — TTS Cache, Loanword Transliteration, Pause Threshold (2026-07-02)

**ทำโดย:** Commander (Claude)
**วันที่:** 2026-07-02
**โปรเจกต์:** `D:\AI-Workspace\projects\friday`
**ต่อจาก:** [handoff/2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md](../handoff/2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md)

---

## 1. 🎯 บริบท

CEO สังเกตว่า Friday ตอบช้า โดยเฉพาะช่วง "พูดเสร็จ → พี่พูดตอบ → กว่าจะขึ้นว่ากำลังแปลงคำพูด" วิเคราะห์ร่วมกันแล้วแบ่งเป็น 4 เฟส เลือกทำ **Phase 1 + 2 ก่อน** เพราะไว ความเสี่ยงต่ำ ไม่แตะ turn-taking หรือ safety-gate logic ที่เพิ่งแก้บั๊กจริงจังไปในเซสชันก่อนหน้า

**เฟสที่ยังไม่ทำ (ดูท้ายไฟล์):** Phase 3 (streaming LLM + sentence-chunked TTS), Phase 4 (VAD/barge-in, local model, wake word)

---

## 2. ✅ สิ่งที่ทำ

### 2a. TTS Cache ทั่วไป (memoize เสียงที่สังเคราะห์แล้ว)

**ปัญหา:** ประโยคยืนยัน/ยกเลิกของ `CONFIRM_GATED` (เช่น "ต้องการล้างถังรีไซเคิลนะคะ ยืนยันไหมคะ") เป็น string คงที่ แต่ถูกยิง edge-tts API ใหม่ทุกครั้งที่พูด

**แก้:** `TTS_CACHE_DIR` ([friday_walkie_talkie.py:35](../src/friday_walkie_talkie.py#L35)) — cache เสียงลงดิสก์ คีย์ด้วย `md5(VOICE_NAME + text)` ([:163](../src/friday_walkie_talkie.py#L163)) ครั้งแรกสังเคราะห์แล้ว copy เก็บไว้ ครั้งถัดไปข้าม engine (ทั้ง edge-tts และ fallback) ไปเล่นไฟล์ cache ตรงๆ

- ทำงานในระดับ `speak()` ก่อนตัดสินใจว่าจะใช้ engine ไหน — คุมทั้ง 2 engine ในจุดเดียว
- ประโยคที่มี arg แปรผัน (ชื่อแอป, คำค้นหา) จะไม่ hit cache ก็ไม่เป็นไร ไม่มีต้นทุนเพิ่ม
- Cache write เป็น best-effort (`try/except`) — เขียนไม่สำเร็จไม่ทำให้พูดไม่ได้
- Cleanup เดิม (`os.remove(audio_file)`) แก้ไม่ให้ลบไฟล์ cache ถาวรทิ้งหลังเล่นจบ

### 2b. Gemma แปลงคำทับศัพท์อังกฤษก่อนเข้า fallback TTS

**ปัญหา (จาก handoff ก่อนหน้า):** VachanaTTS (fallback engine) รับคำอังกฤษดิบปนในประโยค (เช่น `"เปิด notepad ให้แล้วค่ะ"`) แล้วเดาเสียงเอง ออกมาไม่ชัด — แก้ทีละคำด้วย dictionary (`_FALLBACK_TTS_SUBSTITUTIONS`) ไม่ scale เพราะชื่อแอป/คำอังกฤษมีไม่จำกัด

**แก้:** `_transliterate_loanwords()` ([friday_walkie_talkie.py:89](../src/friday_walkie_talkie.py#L89)) เรียก Ollama (gemma) ให้สะกดคำอังกฤษเป็นคำไทยที่ออกเสียงถูกก่อนส่งเข้า `generate_speech_fallback()`

- Skip การเรียกทันทีถ้าไม่มีอักษรอังกฤษเลย (`re.search(r'[A-Za-z]', text)`) — ประโยคไทยล้วนไม่เสีย latency เพิ่ม
- Fail-open: เรียกไม่สำเร็จ (timeout/network) → คืน text เดิม ไม่ทำให้ Friday เงียบ
- **ตั้งใจไม่ reuse `ask_ollama()`** — ฟังก์ชันนั้นเรียก `speak()` เองได้ถ้า response ช้าเกิน 25s (มีไว้เตือน "cloud มีปัญหา") แต่ `_transliterate_loanwords()` ถูกเรียกจากใน `speak()` ขณะถือ `AUDIO_LOCK` (ซึ่งเป็น `threading.Lock()` ธรรมดา ไม่ reentrant) — ถ้า reuse จะเสี่ยง deadlock ตัวเอง จึงเขียน `requests.post` แยกตรงๆ แทน (single attempt, timeout=8s)
- Manual substitution dict (`_FALLBACK_TTS_SUBSTITUTIONS`) ยังอยู่ ทำงานเป็นชั้นสองหลัง LLM แปลงแล้ว (เผื่อ LLM สะกดแบบที่รู้อยู่แล้วว่าออกเสียงผิด เช่น "ฟรายเดย์")

### 2c. `pause_threshold` 1.5s → 0.8s

**ปัญหา:** [friday_walkie_talkie.py:871](../src/friday_walkie_talkie.py#L871) ตั้งไว้รอเงียบ 1.5 วินาทีก่อนตัดจบประโยค (`r.listen()` ไม่ return จนกว่าจะเงียบครบ) — คือช่วงที่ CEO รู้สึกว่า "พูดเสร็จแล้วกว่าจะขึ้นกำลังแปลงคำพูด"

**แก้:** ปรับเป็น 0.8s (ค่า default ของ library `SpeechRecognition`) — **Tradeoff:** ถ้า CEO พูดเว้นจังหวะกลางประโยคบ่อย จะโดนตัดคำ ต้องปรับขึ้นถ้าเจอปัญหานี้จริง

---

## 3. 🧪 เทสที่เพิ่ม

| เทส | ตรวจอะไร |
|---|---|
| `tts_cache_hit_skips_regeneration` | speak() 2 ครั้งด้วย text เดียวกัน → generate_speech ถูกเรียกแค่ครั้งเดียว |
| `transliterate_loanwords_fails_open` | ข้อความไทยล้วนข้าม network call / เรียกไม่สำเร็จคืน text เดิม |

**บั๊กที่เจอระหว่างเขียนเทส:** `check_audio_serialization` กับ `check_speak_uses_fallback_when_edge_tts_fails` เรียก `fw.speak()` จริง ซึ่งตอนนี้เขียน/อ่าน `TTS_CACHE_DIR` แบบไม่มีเงื่อนไข — รันเทสรอบแรกจะสร้าง cache ของ text ทดสอบ (`"test A"`, `"ทดสอบ fallback"`) ทิ้งไว้บนดิสก์จริง ทำให้รันซ้ำรอบ 2 hit cache แล้ว mock ไม่ถูกเรียก เทสพังแบบ non-deterministic — แก้ด้วยการ monkeypatch `fw.TTS_CACHE_DIR` เป็น temp dir ชั่วคราวในทั้งสองเทสนั้น

**ผลทดสอบ:** `test_tools.py` **50/50 passed** — รันซ้ำ 2 รอบติดกันยืนยันไม่มี pollution ข้าม run

---

## 4. ⚠️ ค้างจากก่อนหน้า (ยังไม่เปลี่ยนสถานะ)

- **CEO ต้องทดสอบพูดจริง** "เปิด Notepad" ด้วยเสียง edge-tts ยืนยันบั๊ก `CONFIRM_WORDS` (คำลงท้ายสุภาพ) ไม่วนลูปอีก + สังเกต latency ที่ควรไวขึ้นจาก Phase 1/2 นี้ด้วยในตัว
- Phase 3 (streaming Ollama response + sentence-chunked TTS) — ยังไม่เริ่ม เสี่ยงกระทบ `CONFIRM_GATED` ถ้า parse `tool_calls` แบบ incremental ผิด ต้องวางแผนแยกก่อนลงมือ
- Phase 4 (VAD/interruptible barge-in, local model แทน cloud, wake word/voiceprint) — พักไว้ตามการตัดสินใจเดิม

---

## 5. 🔗 อ้างอิง

- [handoff/2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md](../handoff/2026-07-02-rename-native-tools-tiered-confirm-fallback-voice.md) — เซสชันก่อนหน้า (native tool-calling, tiered confirm-gate, CONFIRM_WORDS bug)
- [WALKTHROUGH.md](WALKTHROUGH.md) — วิธีรัน Friday (conda env `friday`)
