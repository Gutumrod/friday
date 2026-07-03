---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-03-lg-tv-control-tools.md
วันที่: 2026-07-03
ผู้เขียน: Commander (Claude)
---

# Handoff — LG webOS TV control tools (tv_power/tv_volume/tv_launch_app/tv_play_video/tv_remote_button)

ต่อจาก [2026-07-03-camera-vision-tools.md](2026-07-03-camera-vision-tools.md) — session เดียวกัน

## สรุป

CEO อยากให้ Friday คุมรีโมททีวีในบ้านได้ (LG Smart TV, webOS) — ทำ live test บนทีวีจริง
ทั้งหมดก่อนเขียนโค้ด (ตาม Arm 5) แล้วค่อยเขียนเป็น tool จริง

## Live test บนทีวีจริง (ก่อนเขียนโค้ด)

รายละเอียดเต็มอยู่ที่ [lg-tv-control-live-test-2026-07-03.md](../../../agents/claude/notes/lg-tv-control-live-test-2026-07-03.md)
สรุปที่สำคัญ:

- **จับคู่แล้ว** — client-key ถาวร ไม่ต้องขอ pairing ใหม่
- **เปิด/ปิดทีวีทำได้จริง** (power_off + Wake-on-LAN)
- **ปรับเสียง/เปิดแอป/กดปุ่มรีโมทเสมือนทำได้จริงทั้งหมด**
- **เล่นวิดีโอเฉพาะเจาะจงผ่านเสียง — แก้ข้อสรุปที่เคยผิดไปในเซสชันเดียวกัน:** ตอนแรกคิดว่าเป็น
  hard limit เพราะ deep-link เจอหน้าเลือกโปรไฟล์ทุกครั้ง แต่ที่จริงแค่ต้องส่ง `ok()` ตามหลัง
  deep-link ไม่กี่วินาที ก็เล่น content ที่ขอไว้ได้จริง — พิสูจน์ end-to-end กับเพลงจริง
  ("HONNE - Day 1") สำเร็จ ไม่มีคนช่วยกดเลย

## สิ่งที่ทำ (โค้ด)

- **`_tv_connect()`** — connect + register ด้วย `TV_CLIENT_KEY` ที่จับคู่ไว้แล้ว มี socket
  timeout กันไม่ให้ Friday ค้างทั้งเสียงถ้าทีวีปิด/ต่อเน็ตไม่ติด
- **`tool_tv_power`** — on = Wake-on-LAN, off = `SystemControl.power_off()`
- **`tool_tv_volume`** — up/down/mute ผ่าน `MediaControl` (คนละตัวกับ `tool_set_volume` เดิมที่คุมเสียงเครื่อง PC)
- **`tool_tv_launch_app`** — เปิดแอปด้วยชื่อ match กับ `list_apps()` ของทีวีเอง ไม่ hardcode app-id map
- **`tool_tv_play_video`** — ค้นด้วย `yt-dlp` (`ytsearch1`, แม่นกว่า web search ทั่วไปที่ลองก่อน)
  แล้วรัน sequence ที่พิสูจน์แล้ว (home→deep-link→รอ 5 วิ→ok) return ชื่อเพลงที่เจอกลับมาด้วย
  ให้ Friday พูดทวน (CEO ขอเพิ่ม — เผื่อหาผิดเพลงจะได้รู้ทันที)
- **`tool_tv_remote_button`** — กดปุ่มตามชื่อ (whitelist จาก `InputControl.INPUT_COMMANDS`
  ตัดพวก move/click/scroll ออกเพราะเป็นคำสั่งเมาส์เสมือน ไม่ใช่ปุ่มที่เสียงจะสั่งชื่อได้)
- ทั้ง 5 ตัว **CONFIRM_GATED ทั้งหมด** — ตามนโยบายเดิมของโค้ด (ทุก tool ที่มีผลจริงต้องถามยืนยัน
  เหมือน set_volume/media_control/open_app)
- เพิ่ม dependency ใหม่ 2 ตัว: `pywebostv`, `yt-dlp` — ติดตั้งเข้า conda env `friday` จริงแล้ว
  (บทเรียนจาก opencv-python รอบก่อน: ต้องลงใน env จริง ไม่ใช่แค่ python บน PATH)

## ทดสอบ

**61/61 passed** (58 เดิม + 3 ใหม่ mock `pywebostv`/`yt-dlp` ทั้งหมด ไม่ต้องมีทีวีจริงตอนรัน CI)

**Live-verified กับทีวีจริงด้วย:** `tool_tv_volume` เรียกจริงผ่านไฟล์ `friday_walkie_talkie.py`
โดยตรง (ไม่ใช่ script แยกทดสอบ) — เสียงขึ้น 10 แล้วลงกลับ 9 ปกติ ระหว่างเพลงกำลังเล่นอยู่
ไม่รบกวน

## ค้างจากก่อนหน้า (ไม่เปลี่ยนสถานะ)

เหมือน handoff ก่อนหน้าทั้งหมด — ยังไม่มีอะไรเปลี่ยนสถานะจากตัวนี้ (ไมค์จริง, Test 2 stress,
Windows Thai SAPI voice หลังรีสตาท, Phase 3/4, Telegram, macOS porting)

## ลงชื่อ

Commander (Claude) — session 2026-07-03
