# Rollback Point ก่อนเริ่ม Live-Migration — 2026-07-03

**บริบท:** ก่อนเริ่ม Phase A ของ [LIVE_UPGRADE_PLAN_2026-07-03.md](LIVE_UPGRADE_PLAN_2026-07-03.md) (ย้ายไป Gemini Live API) CEO สั่งให้แบคอัพทุกอย่างไว้ก่อน เผื่อวันไหนอยากถอยกลับมาเป็นเวอร์ชัน local walkie-talkie (เดิม/ปัจจุบัน) จะได้รีย้อนกลับได้ทันที

## จุดที่แบคอัพไว้

1. **โค้ด → GitHub**
   - Commit: `cfd10e3` (branch `master`, https://github.com/Gutumrod/friday)
   - รวม fix ล่าสุดก่อนแบคอัพ: `TV_IP` ที่ค้าง (.134 → .107), `tool_tv_power` verify-after-WoL, `_is_confirm` (compound confirm phrase), gender-consistency ใน search-summary system stub — ดู commit message สำหรับรายละเอียด

2. **ทั้งโปรเจค (รวมส่วนที่ `.gitignore` ไม่ครอบ)** → mirror เต็มด้วย `robocopy /MIR`
   - ตำแหน่ง: `D:\AI-Workspace\backups\friday_2026-07-03_1900`
   - ขนาด: ~126 MB, 282 ไฟล์
   - **สำคัญ:** นี่คือที่เดียวที่มี `vault/` (ความจำจริงของ Friday — `facts.md` + ประวัติการสนทนาทุก session), `voices/`, `tts_cache/`, `backups/` เพราะทั้งหมดนี้ไม่ได้ push ขึ้น git (อยู่ใน `.gitignore`)

## วิธีถอยกลับ (rollback)

- **ถอยแค่โค้ด:** `git checkout cfd10e3` (หรือ `git reset --hard cfd10e3` ถ้าต้องการทิ้งทุกอย่างหลังจากนี้) — **ไม่คืน** `vault/`/`voices/`/`tts_cache/`
- **ถอยทั้งโปรเจครวมความจำจริง:** คัดลอกทั้งโฟลเดอร์ `D:\AI-Workspace\backups\friday_2026-07-03_1900` กลับไปทับ `D:\AI-Workspace\projects\friday` (หรือ mirror กลับด้วย robocopy ทิศทางย้อนกลับ)

## ทำไมต้องมี 2 ชั้น

Git เก็บแค่โค้ด ไม่เก็บ runtime state (จงใจ ตาม `.gitignore`) ถ้าใช้แค่ git rollback จะได้โค้ดเก่ากลับมาแต่ **เสียความจำ/ประวัติการคุยของ Friday ไปเลย** — การ mirror เต็มคือทางเดียวที่กู้ทั้งคู่กลับมาพร้อมกันได้
