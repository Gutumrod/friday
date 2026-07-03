# กล้องเว็บแคม + คุมทีวี LG ผ่านเสียง (2026-07-03)

**ทำโดย:** Commander (Claude)
**วันที่:** 2026-07-03
**โปรเจกต์:** `D:\AI-Workspace\projects\friday`
**ต่อจาก:** [TIMER_RESILIENCE_AND_JARVIS_WARNING_2026-07-02.md](TIMER_RESILIENCE_AND_JARVIS_WARNING_2026-07-02.md) — คนละเซสชัน คนละแกนงาน (ฟีเจอร์ใหม่ 2 ชิ้น ไม่เกี่ยวกับ timer/latency)

---

## 1. 🎯 บริบท

สองฟีเจอร์แยกกัน คุยต่อเนื่องในเซสชันเดียว:

1. CEO ถามว่าเครื่องมีเว็บแคมติดอยู่ ต่อให้ Friday เปิดกล้องดูภาพได้ไหม — สรุปว่าไม่เอาแบบ
   Gemini Live (สตรีมต่อเนื่อง), เอาแบบ **2 trigger แยกกัน**: สั่งเปิดกล้อง แล้วค่อยถามว่าเห็นอะไรทีหลัง
2. CEO อยากให้คุมรีโมททีวีในบ้าน (LG Smart TV, webOS) ผ่านเสียง — ทำ **live test บนทีวีจริงก่อนเขียนโค้ด**
   (ตาม Arm 5) ผ่าน python -c ตรงๆ ทีละคำสั่ง มี CEO คอยดูจอ/ยืนยันผลสดๆ

---

## 2. ✅ กล้องเว็บแคม (`open_camera` / `look_camera` / `close_camera`)

**ดีไซน์:** snapshot-on-ask ไม่ใช่ streaming — `open_camera` เปิดกล้องทิ้งไว้ (`_camera` global,
[friday_walkie_talkie.py:842](../src/friday_walkie_talkie.py#L842)), `look_camera`
([:884](../src/friday_walkie_talkie.py#L884)) ถ่าย 1 เฟรมจากกล้องที่เปิดอยู่แล้วส่งเข้า
`gemma4:31b-cloud` (ยืนยันแล้วว่ารับภาพได้) ผ่าน `_ask_ollama_vision()` ใหม่ (เรียก Ollama ตรง
ไม่ผ่าน `ask_ollama()` เพราะไม่มี history/tools) — ยิงเฉพาะตอนถูกถามจริง ไม่มี poll ต่อเนื่อง

- **`open_camera` เท่านั้นที่ CONFIRM_GATED** — เหตุผลเดียวกับ `clipboard_read`: เปิดกล้องเองโดย
  ไม่ตั้งใจจากเสียงที่ฟังผิดเป็นความเสี่ยง privacy ส่วน `look_camera`/`close_camera` ungated
  ตามที่ CEO ขอ (ไม่ให้ถามซ้ำทุกครั้งที่ถามว่า "เห็นอะไร")
- **`CAMERA_INDEX`** ([:37](../src/friday_walkie_talkie.py#L37)) เป็น config constant แยก
  ไม่ hardcode `0` ในฟังก์ชัน — ตามแพทเทิร์นเดียวกับ `DEVICE_INDEX` ของไมค์ (ค่าต่างเครื่องได้
  ถ้าเอาไปแชร์ให้คนอื่นใช้ในอนาคต)
- เพิ่ม `opencv-python` เป็น dependency ใหม่ **และติดตั้งเข้า conda env `friday` จริงแล้ว**
  (ไม่ใช่แค่ python บน PATH — บทเรียนที่พลาดไปทีแรกก่อนแก้)

**Live-verified:** เปิดกล้องจริง โมเดลอธิบายภาพห้องออกมาถูกต้อง (เห็นเก้าอี้ขาว พัดลม ตะกร้า)

---

## 3. ✅ คุมทีวี LG webOS (`tv_power` / `tv_volume` / `tv_launch_app` / `tv_play_video` / `tv_remote_button`)

### การค้นพบระหว่าง live test (ก่อนเขียนโค้ด)

- เจอทีวีบน LAN ที่ `192.168.1.134` เปิดพอร์ต webOS SSAP (`3000`/`3001`, ต้องใช้ `3001`/wss
  เท่านั้น — `3000` เจอ connection reset)
- Pairing ผ่าน `pywebostv` ได้ client-key ถาวร ไม่ต้องขอใหม่ทุกครั้ง
- **เล่นวิดีโอเฉพาะเจาะจงผ่าน deep-link — ตอนแรกสรุปผิดว่าเป็น hard limit** เพราะทดสอบแค่
  `launch(params={'contentTarget': url})` เดี่ยวๆ (4 รอบ ผลเหมือนเดิมทุกครั้ง: เด้งไปหน้าเลือก
  โปรไฟล์ YouTube) **ที่จริงคือ**: หน้าเลือกโปรไฟล์ไม่ได้ทิ้ง deep-link ที่ pending อยู่ — แค่ต้อง
  ส่ง `ok()` ตามหลัง deep-link อีกทีก็เล่น content ที่ขอไว้ทันที พิสูจน์ end-to-end กับเพลงจริง
  ("HONNE - Day 1") สำเร็จ ไม่มีคนช่วยกดเลย
- Chromecast/DIAL (พอร์ต 8008/8009) — **ทีวีเครื่องนี้ไม่รองรับ** ปิดทางลัดนี้ไป
- IME `insertText` (พิมพ์ผ่าน API) **ใช้กับคีย์บอร์ดที่ YouTube วาดเองไม่ได้** เป็นคำสั่งระดับ OS
  ใช้ได้แค่ช่องพิมพ์ของระบบเท่านั้น — ต้องพิมพ์ทีละตัวผ่าน d-pad ถ้าไม่ใช้ deep-link
- รายละเอียดดิบทั้งหมด (ทุกคำสั่งที่ลอง/พลาด/สำเร็จ): [lg-tv-control-live-test-2026-07-03.md](../../../agents/claude/notes/lg-tv-control-live-test-2026-07-03.md)

### โค้ด

- **`_tv_connect()`** ([friday_walkie_talkie.py:905](../src/friday_walkie_talkie.py#L905)) —
  connect + register ด้วย `TV_CLIENT_KEY` ที่จับคู่ไว้แล้ว มี socket timeout
  (`TV_CONNECT_TIMEOUT`) กันไม่ให้ Friday ค้างทั้งเสียงถ้าทีวีปิด/ต่อเน็ตไม่ติด
- **`tool_tv_power`** — `on` = Wake-on-LAN magic packet, `off` = `SystemControl.power_off()`
- **`tool_tv_volume`** — up/down/mute ผ่าน `MediaControl` (คนละตัวกับ `tool_set_volume` เดิม
  ที่คุมเสียงเครื่อง PC นี้ ไม่ใช่เสียงทีวี)
- **`tool_tv_launch_app`** — เปิดแอปด้วยชื่อ match กับ `list_apps()` ของทีวีเอง ไม่ hardcode
  app-id map (กันพังถ้าทีวีอัปเดต/มีแอปเพิ่ม)
- **`tool_tv_play_video`** ([:983](../src/friday_walkie_talkie.py#L983)) — ค้นด้วย `yt-dlp`
  (`ytsearch1`, ค้นตรงในระบบ YouTube เอง แม่นกว่า generic web search ที่ลองก่อน — เทียบแล้ว
  ตาม 2-of-3 rule) แล้วรัน sequence ที่พิสูจน์แล้ว (home→launch deep-link→รอ 5 วิ→ok) return
  ชื่อเพลงที่เจอกลับมาด้วยให้ Friday พูดทวน (CEO ขอเพิ่ม — เผื่อหาผิดเพลงจะได้รู้ทันที ไม่ต้อง
  ถามยืนยันซ้ำเพราะแก้ไขง่ายแค่บอกเปลี่ยนเพลง)
- **`tool_tv_remote_button`** — กดปุ่มตามชื่อ, whitelist จาก `InputControl.INPUT_COMMANDS`
  (`_TV_BUTTONS`, [:1028](../src/friday_walkie_talkie.py#L1028)) ตัด `move`/`click`/`scroll`
  ออกเพราะเป็นคำสั่งเมาส์เสมือน ไม่ใช่ปุ่มที่เสียงจะสั่งชื่อได้
- **ทั้ง 5 ตัว CONFIRM_GATED** — ตามนโยบายเดิมของโค้ด (ทุก tool ที่มีผลจริงต้องถามยืนยัน เหมือน
  `set_volume`/`media_control`/`open_app`)
- เพิ่ม dependency ใหม่ 2 ตัว: `pywebostv`, `yt-dlp` — ติดตั้งเข้า conda env `friday` จริงแล้ว

### จุดที่ตั้งใจไม่ทำ

- ไม่ยัด logic "แก้ query คลุมเครือ" ใดๆ เพิ่ม (เช่น ลองหลายคำค้น/ให้โมเดลคัดกรองผลลัพธ์) —
  2-of-3 คำค้นทดสอบตรงพอแล้ว ถ้าเจอปัญหาจริงในหน้างานค่อยกลับมาแก้
- ไม่ทำ mapping ชื่อแอปแบบตายตัว (hardcoded id map) — ใช้ `list_apps()` สดจากทีวีเสมอ

---

## 4. 🧪 เทสที่เพิ่ม/แก้

| เทส | ตรวจอะไร |
|---|---|
| `camera_gate_wiring` | `open_camera` อยู่ใน `CONFIRM_GATED` ถูกต้อง, `look_camera`/`close_camera` ไม่ถูก gate |
| `camera_open_look_close_roundtrip` | open(no-op ซ้ำ)→look(refuse ก่อน open)→close(idempotent) ด้วย fake `cv2.VideoCapture` |
| `tv_gate_wiring` | tv_* ทั้ง 5 ตัวอยู่ใน `CONFIRM_GATED` ถูกต้อง |
| `tv_power_volume_launch_roundtrip` | on/off/invalid, up/mute, launch(found/missing) ด้วย fake pywebostv Control classes |
| `tv_play_video_and_remote_button` | sequence home→launch(deep-link)→ok ตรงลำดับ ด้วย fake `yt-dlp`/`InputControl`, ปุ่ม valid/invalid |
| `pack_args` (แก้เพิ่ม) | เพิ่มเคส `look_camera`/`tv_power`/`tv_play_video` |

**ยืนยันด้วยมือเพิ่ม (นอกชุดเทสอัตโนมัติ, กับกล้อง/ทีวีจริง):**
1. `tool_open_camera`/`tool_look_camera`/`tool_close_camera` จริงกับกล้องเครื่องนี้ — อธิบายภาพห้องถูกต้อง
2. `tool_tv_volume('up'/'down')` จริงกับทีวี — เสียงขึ้น 10 ลงกลับ 9 ไม่รบกวนเพลงที่เล่นอยู่
3. `tool_tv_power('off')` จริง — ปิดทีวีจริง
4. **End-to-end เต็มรูปแบบ:** `tool_tv_power('on')` → รอบูต → `tool_tv_play_video(...)` สั่งเปิด
   "โดนของเขมร • คุณกาน | 30 ก.ค. 66 | THE GHOST RADIO" ผ่านโค้ดจริงในไฟล์ (ไม่ใช่ script แยก) —
   เล่นคลิปที่ขอถูกต้อง

**ผลทดสอบอัตโนมัติ:** `test_tools.py` **61/61 passed**

---

## 5. ⚠️ ยังไม่ครอบคลุม

- **พิมพ์ค้นหา/นำทาง on-screen keyboard แบบ blind** (ไม่ใช้ deep-link) — ทำได้แค่กด d-pad ทีละตัว
  ต้องมีคน narrate ตำแหน่ง highlight ตลอด เพราะ Friday มองจอทีวีไม่เห็น (แก้ไม่ได้ด้วยโค้ดตอนนี้
  ถ้าอยากทำจริงต้องเอากล้อง `look_camera` ที่เพิ่งทำไปวันนี้มาช่วยดูจอทีวีแทนคน — ยังไม่ได้ทำ)
- ไม่ได้ทดสอบ deep-link+ok sequence กับแอปอื่นนอกจาก YouTube (เช่น Netflix) — ไม่รู้ว่า
  behaviour เดียวกันไหม
- ดีเลย์ 3s/5s ใน sequence เป็นค่าที่ทดสอบผ่านแค่ 2 รอบ (ปกติ + หลัง WoL) ยังไม่ได้ stress-test
  ว่าพอสำหรับทุกกรณี (เช่น เน็ตช้ากว่านี้)

---

## 6. 🔗 อ้างอิง

- [lg-tv-control-live-test-2026-07-03.md](../../../agents/claude/notes/lg-tv-control-live-test-2026-07-03.md) — log ดิบเต็มของ live test บนทีวีจริง รวมข้อสรุปที่ผิดแล้วแก้ทีหลัง
- [handoff/2026-07-03-camera-vision-tools.md](../handoff/2026-07-03-camera-vision-tools.md)
- [handoff/2026-07-03-lg-tv-control-tools.md](../handoff/2026-07-03-lg-tv-control-tools.md)
- [TIMER_RESILIENCE_AND_JARVIS_WARNING_2026-07-02.md](TIMER_RESILIENCE_AND_JARVIS_WARNING_2026-07-02.md) — เซสชันก่อนหน้า
