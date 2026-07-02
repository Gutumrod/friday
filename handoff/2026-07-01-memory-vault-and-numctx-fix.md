---
path: D:\AI-Workspace\projects\jarvis\handoff\2026-07-01-memory-vault-and-numctx-fix.md
วันที่: 2026-07-01
ผู้เขียน: Commander (Claude)
---

# Handoff — Friday: Memory Vault + num_ctx Fix, พร้อมเข้า Phase 2 (Tool Integration)

## สรุปสิ่งที่ทำในเซสชันนี้

1. **รีวิวโค้ด** `friday_walkie_talkie.py` (สร้างโดย Antigravity) — ไม่มีบั๊กบล็อกการทำงาน, deps/model ทั้งหมด verify แล้วว่ามีจริง
2. **สร้าง memory vault** ที่ `vault/` (Obsidian-compatible, แยกจาก Vault หลักตามที่นายสั่ง):
   - `vault/facts.md` — fact เกี่ยวกับนายที่ inject เข้า system prompt ทุกครั้งที่เปิดโปรแกรม
   - `vault/history/YYYY-MM-DD.md` — log บทสนทนาอัตโนมัติทุก turn
3. **เปลี่ยนคำเรียกผู้ใช้** จาก "คุณฟรี" → **"นาย"** ทั้งใน system prompt, คำทักทาย, ข้อความปิดเครื่อง, error message (sync กับ facts.md)
4. **แก้ `num_ctx: 2048 → 16000`** ที่ [friday_walkie_talkie.py](file:///D:/AI-Workspace/projects/jarvis/friday_walkie_talkie.py) — ค่าเดิมตั้งไว้ตอนวางแผนใช้ `ornith:9b` (local, ต้องกัน VRAM) แต่โปรเจกต์สลับมาใช้ `gemma4:31b-cloud` (คลาวด์ ไม่ใช้ GPU เครื่องนี้ รองรับ context ถึง 262144) แล้วไม่มีใครอัปเดตค่าตาม — เป็นสาเหตุที่ Friday เริ่มสับสน/ลืมบทสนทนาเมื่อคุยยาว
5. **ทดสอบ end-to-end จริง** — นายรันเองผ่านไมค์ คุยได้ลื่น เสียงเป็นธรรมชาติขึ้น
6. **สำรวจ ChindaTTS (iApp Technology)** เป็นทางเลือกแทน edge-tts — Thai TTS คุณภาพสูงกว่า มี style control แต่เสียเงิน (1 credit/400 ตัวอักษร, มี 50 credit ฟรีทดลอง) ยังไม่ได้ตัดสินใจเปลี่ยน

## จุดที่ตัดสินใจไปแล้ว (ไม่ต้องทำต่อ)

- **Fallback ไป `ornith:9b`** ที่ PRD.md ตาราง Risks พูดถึง — Antigravity เขียนไว้เผื่อเฉยๆ **นายยืนยันแล้วว่าไม่ได้ตั้งใจจะทำ** ไม่ต้อง implement fallback logic หรือ per-model `num_ctx`

## ROADMAP ถัดไป — Phase 2: Tool Integration (ตามที่นายสั่งให้เตรียมทำต่อ)

อ้างอิงจาก [PRD.md](file:///D:/AI-Workspace/projects/jarvis/PRD.md) และ [PROJECT_CONTEXT.md](file:///D:/AI-Workspace/projects/jarvis/PROJECT_CONTEXT.md) (เขียนโดย Antigravity):

- [ ] Tool parser อ่านคำสั่งพิเศษจาก Friday เช่น `[TOOL: send_telegram("...")]`
- [ ] เชื่อมส่งงานเข้า Hermes Mailbox (`D:\AI-Workspace\mailbox\inbox\hermes\`)
- [ ] คำสั่งพื้นฐานในเครื่อง (เช็คดิสก์, เปิดเบราว์เซอร์, เปิดแอป)
- [ ] อัปเดต prompt ให้ Friday ตอบตามผลจริงของการเรียก tool (สำเร็จ/ขัดข้อง)

**คำแนะนำจาก session นี้ (ยังไม่ได้ทำ):** `gemma4:31b-cloud` รองรับ native tool-calling ของ Ollama อยู่แล้ว (capability `tools` confirmed จาก `/api/tags`) — แนะนำให้ใช้ Ollama tools API (ส่ง `tools` schema ใน payload) ควบคู่กับ/แทนการ parse tag `[TOOL: ...]` จากข้อความล้วน จะแม่นกว่าและลด hallucinate การเรียก tool ผิด

## ไฟล์ที่แก้/สร้างในเซสชันนี้

- `friday_walkie_talkie.py` — vault integration + num_ctx fix + เปลี่ยนคำเรียก
- `vault/facts.md`, `vault/history/` — สร้างใหม่
- ไฟล์นี้ (handoff)

## ถัดไป

รอนายสั่งเริ่ม Phase 2 — เมื่อเริ่ม ให้อ่านไฟล์นี้ + PRD.md + PROJECT_CONTEXT.md ก่อนลงมือ

## ลงชื่อ

Commander (Claude) — session 2026-07-01
