---
path: D:\AI-Workspace\projects\friday\handoff\2026-07-19-tv-connect-preflight-and-startup-live-test.md
วันที่: 2026-07-19
ผู้เขียน: Codex
---

# Handoff - Startup live test and TV connect preflight

## สรุป

ต่อจาก `handoff/2026-07-19-voice-latency-phrase-bank-and-ungated-tool-wire.md`

- ยืนยันว่า commit ก่อนหน้า push แล้ว: `b5e87dc feat: add Friday voice latency phrase bank`
- live test startup choreography ผ่าน:
  - `สวัสดีค่ะนาย`
  - `ขอเช็คไมค์กับวอร์มเสียงแป๊บนึงค่ะ`
  - calibrate mic
  - `พร้อมฟังค่ะนาย`
  - เริ่ม listen แล้วค่อย warm up JaiTTS background
- TV IP เดิม `192.168.1.107` ไม่ reachable ตอนทดสอบ:
  - `Test-Connection`: false
  - TCP `192.168.1.107:3001`: timeout
- พบว่า `_tv_connect()` ก่อนแก้สามารถเกิน timeout ที่ตั้งใจไว้ เพราะ `pywebostv/ws4py` ยังเข้า connect path ยาวได้
- แก้ให้ `_tv_connect()` ทำ TCP preflight ด้วย `socket.create_connection((TV_IP, 3001), timeout=TV_CONNECT_TIMEOUT)` ก่อนสร้าง `WebOSClient`
- TV tools ที่ connect ไม่ได้คืน phrase ปลอดภัยแทน raw exception:
  - `ดูเหมือนทีวีจะไม่ได้เปิดเครื่องหรือหลุดจากการเชื่อมต่อเครือข่ายค่ะ ลองเช็คปลั๊กหรือไวไฟดูนะคะ`
- `_verify_tv_on()` ใช้ phrase bank `tv_error_wol_check` แทน hard-coded text

## ไฟล์ที่แก้

- `src/friday/core.py`
- `src/test_tools.py`
- `handoff/2026-07-19-tv-connect-preflight-and-startup-live-test.md`

## Validation

ใช้ Python env:

`C:\Users\Win10\miniconda3\envs\friday\python.exe`

ผล:

- `python -m py_compile src\friday\core.py src\test_tools.py src\friday\phrases.py src\friday\latency.py` passed
- `src\test_tools.py`: 76/76 passed
- `src\test_api.py`: 2 tests OK
- live `_tv_connect()` หลัง patch:
  - `CONNECT_FAIL ms=5000.4 ConnectionError: ดูเหมือนทีวีจะไม่ได้เปิดเครื่องหรือหลุดจากการเชื่อมต่อเครือข่ายค่ะ ลองเช็คปลั๊กหรือไวไฟดูนะคะ`

Known warnings เดิม:

- Google Cloud STT quota exceeded ระหว่าง fallback tests แต่ tests ผ่าน
- Google API Python 3.10 future support warning
- HuggingFace unauthenticated warning
- mocked/corrupt audio warnings จาก test behavior เดิม

## Next Work

1. ถ้าจะ debug TV ต่อ ต้องหา source of truth ใหม่ก่อนว่า LG TV ได้ IP อะไรจริงตอนนี้:
   - router DHCP lease
   - LG TV network settings
   - network scan ใน subnet
2. เมื่อได้ IP ใหม่แล้วค่อย test read-only:
   - port `3001`
   - `_tv_connect()`
   - `ApplicationControl(client).list_apps()`
3. ถ้า connect ได้ ค่อย live test gated TV tools ผ่าน Friday voice flow:
   - `tv_launch_app("youtube")`
   - `tv_play_video("<query>")`
4. อย่า hardcode IP ใหม่จากการเดา ต้องมีหลักฐานจากเครื่อง/TV/router ก่อน
