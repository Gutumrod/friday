# Hermes — Friday Project Restructure (2026-07-02)

**ทำโดย:** Hermes Agent  
**วันที่:** 2026-07-02  
**โปรเจกต์:** `D:\AI-Workspace\projects\friday`

---

## 1. 📁 โครงสร้างโฟลเดอร์ใหม่

```
friday/
├── src/
│   ├── friday_walkie_talkie.py   ← ไฟล์หลัก
│   └── test_tools.py             ← ชุดทดสอบ
├── docs/
│   ├── PRD.md
│   ├── WALKTHROUGH.md
│   ├── FRIDAY_UI_DESIGN.md
│   ├── PROJECT_CONTEXT.md
│   ├── RENAME_CHANGELOG.md
│   └── HERMES_RESTRUCTURE_2026-07-02.md  ← ไฟล์นี้
├── audit/
│   └── FRIDAY_AUDIT.md
├── handoff/                      ← ประวัติการทำงาน 4 ไฟล์
├── backups/                      ← .bak-* ทั้งหมด 15 ไฟล์
├── vault/                        ← facts.md + history/
├── requirements.txt
└── __pycache__/
```

### สิ่งที่ย้าย

| จาก (root) | ไปยัง | หมายเหตุ |
|------------|-------|----------|
| `friday_walkie_talkie.py` | `src/` | ไฟล์หลัก |
| `test_tools.py` | `src/` | ชุดทดสอบ |
| `PRD.md`, `WALKTHROUGH.md`, `FRIDAY_UI_DESIGN.md`, `PROJECT_CONTEXT.md`, `RENAME_CHANGELOG.md` | `docs/` | เอกสาร |
| `*.bak-*` 15 ไฟล์ | `backups/` | backup เก่า ไม่ลบ |

---

## 2. 🔧 แก้ไข Path หลังย้ายไฟล์

**ไฟล์:** `src/friday_walkie_talkie.py` — บรรทัดที่ 30

**ปัญหา:** `VAULT_DIR` คำนวณจาก `os.path.dirname(__file__)` ซึ่งหลังย้ายเข้า `src/` แล้ว path ชี้ไปที่ `src/vault/` แทน `friday/vault/`

**ก่อน:**
```python
VAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vault")
# → D:\AI-Workspace\projects\friday\src\vault\  ❌
```

**หลัง:**
```python
VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault")
# → D:\AI-Workspace\projects\friday\vault\  ✅
```

**ผลกระทบ:** `remember()` tool, session history, facts.md — ทั้งหมดทำงานถูกต้อง

---

## 3. ✅ ผลทดสอบหลังแก้ไข

```
38/38 PASSED
```

ทุก test ผ่าน รวมถึง:
- `remember` (เดิมพังเพราะหา vault ไม่เจอ)
- `native_tool_calling(live)` — เรียก tool จริงได้
- `confirm_words_added` — confirm gate ทำงาน
- `audio_serialization` — ไม่มี race condition

---

## 4. 📌 สิ่งที่ต้องรู้ก่อน push git

- **`.gitignore` ต้องมี:** `__pycache__/`, `friday_temp_response.mp3`
- **`backups/`** — 15 ไฟล์ .bak-* ควร ignore หรือ commit ก็ได้ (เป็นประวัติ)
- **`vault/`** — ยังไม่ตัดสินใจ ต้องถาม CEO ก่อน
- **GitHub account:** `Gutumrod` — พร้อม push เมื่อ CEO บอก

---

## 5. 🔗 อ้างอิง

- [RENAME_CHANGELOG.md](RENAME_CHANGELOG.md) — Claude เปลี่ยนชื่อ Jarvis → Friday
- [FRIDAY_AUDIT.md](../audit/FRIDAY_AUDIT.md) — Audit ฉบับเต็ม
