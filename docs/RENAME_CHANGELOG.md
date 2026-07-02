# Rename: jarvis → friday (2026-07-02)

โฟลเดอร์โปรเจกต์เปลี่ยนชื่อจาก `D:\AI-Workspace\projects\jarvis` เป็น `D:\AI-Workspace\projects\friday` เหตุผล: ชื่อจริงในระบบ (สคริปต์ ตัวละคร conda env) คือ "Friday" มาตลอด "jarvis" เป็นแค่ชื่อโฟลเดอร์ตอนตั้งโปรเจกต์แรกๆ

## ก่อนเปลี่ยน — เช็คแล้วว่าไม่พัง

ไม่มี hardcoded path ผูกกับชื่อ `jarvis` เลยสักจุด:
- `friday_walkie_talkie.py` คำนวณ `VAULT_DIR`/`FACTS_PATH`/`HISTORY_DIR` จาก `os.path.dirname(os.path.abspath(__file__))` ทั้งหมด — ย้ายโฟลเดอร์ไปไหนก็ทำงานถูก
- ไม่มี launcher (`.vbs`/`.bat`/`.ps1`), shortcut, Windows Scheduled Task, หรือ config ระดับ workspace (`.mcp.json`, `AGENTS.md`, root `CLAUDE.md`) อ้างอิง path นี้เลย
- ไม่มี process รันค้างอยู่ตอนเปลี่ยนชื่อ

## สิ่งที่เปลี่ยน

1. **Rename โฟลเดอร์:** `projects/jarvis` → `projects/friday`
2. **ทดสอบยืนยันหลัง rename:** รัน `test_tools.py` จาก path ใหม่ — **38/38 ผ่านเหมือนเดิม** ไม่มีอะไรพัง
3. **อัปเดตเอกสารอ้างอิง path** (ที่ยังใช้งานอยู่จริง ไม่ใช่ประวัติ):
   - [WALKTHROUGH.md](file:///D:/AI-Workspace/projects/friday/WALKTHROUGH.md) — คำสั่ง `cd` และลิงก์ไฟล์ทั้งหมด
   - [PRD.md](file:///D:/AI-Workspace/projects/friday/PRD.md) — ลิงก์ไฟล์สคริปต์หลัก
   - [PROJECT_CONTEXT.md](file:///D:/AI-Workspace/projects/friday/PROJECT_CONTEXT.md) — ตารางไฟล์สำคัญในโปรเจค (5 path)
   - [audit/FRIDAY_AUDIT.md](file:///D:/AI-Workspace/projects/friday/audit/FRIDAY_AUDIT.md) — หัวเอกสาร + project path

## สิ่งที่ตั้งใจ**ไม่**แก้

- **`handoff/*.md`** — ทุกไฟล์เป็นบันทึกประวัติ (session log ที่มี timestamp) ลิงก์ข้างในชี้ path เก่า `projects/jarvis` ตอนนี้จะเป็นลิงก์ตาย แต่เนื้อหาสะท้อนความจริง ณ เวลาที่เขียน ไม่แก้ย้อนหลัง — ถ้าจะตามลิงก์ในไฟล์เก่า ให้เปลี่ยน `jarvis` → `friday` เองใน path ตอนเปิด
- **`friday_walkie_talkie.py.bak-*`** — ไฟล์ backup ทุกอันเป็น snapshot ตามเวลา ไม่แก้ย้อนหลังเช่นกัน
- **คำว่า "JARVIS+FRIDAY" ใน system prompt** (`friday_walkie_talkie.py:618`) — อันนี้คือคำบรรยาย persona (ลูกผสมสไตล์ JARVIS+FRIDAY ของไอรอนแมน) ไม่ใช่ path ไม่เกี่ยวกับชื่อโฟลเดอร์ ไม่แตะ

## Housekeeping ที่เหลือ

- Memory ของ Claude (`project_jarvis_friday_walkie_talkie.md`) ยังมี path เก่าอยู่ — อัปเดตแล้วพร้อมกับ changelog นี้

## อัปเดต (2026-07-02 ช่วงถัดมา) — Hermes จัดโครงสร้างย่อยใหม่

Hermes ย้ายไฟล์เข้า `src/`/`docs/`/`backups/` ต่อจากนี้ (ดู [HERMES_RESTRUCTURE_2026-07-02.md](HERMES_RESTRUCTURE_2026-07-02.md) รายละเอียดเต็ม) — ตรวจสอบแล้วว่าจริง (ไม่ใช่แค่เขียนในเอกสาร): `test_tools.py` รันจาก `src/` จริง **38/38 ผ่าน**, `VAULT_DIR` แก้ path (`dirname` สองชั้น) ถูกต้องจริง ยืนยันด้วยการ import สคริปต์แล้ว print ค่าออกมาตรง

ลิงก์ที่แก้ไว้ในรายการ "สิ่งที่เปลี่ยน" ข้างบน (WALKTHROUGH.md/PRD.md/PROJECT_CONTEXT.md/audit) **เพี้ยนหลังการย้ายนี้** เพราะ path เอกสารเปลี่ยนจาก root ไป `docs/` และสคริปต์หลักย้ายไป `src/` — Claude แก้ซ้ำอีกรอบให้ตรงโครงสร้างใหม่แล้ว (คำสั่งรันใน WALKTHROUGH.md ก็ปรับเป็น `python.exe src\friday_walkie_talkie.py` ด้วย)
