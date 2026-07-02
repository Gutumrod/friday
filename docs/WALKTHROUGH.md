# Walkthrough: Friday Turn-based AI Assistant

เราได้สร้างโครงร่างและติดตั้งระบบสำหรับผู้ช่วยเสียง **Friday (F.R.I.D.A.Y.)** โหมดสลับกันพูด (Walkie-Talkie) เรียบร้อยแล้ว

## การเปลี่ยนแปลงที่เสร็จสมบูรณ์

1.  **การติดตั้งโฟลเดอร์โปรเจกต์:** สร้างไดเรกทอรีใหม่ที่ [friday](file:///D:/AI-Workspace/projects/friday) (เดิมชื่อ `jarvis` เปลี่ยนชื่อโฟลเดอร์เป็น `friday` เมื่อ 2026-07-02 — ดู [RENAME_CHANGELOG.md](file:///D:/AI-Workspace/projects/friday/docs/RENAME_CHANGELOG.md); Hermes จัดโครงสร้างย่อยใหม่วันเดียวกันเป็น `src/`/`docs/`/`backups/` — ดู [HERMES_RESTRUCTURE_2026-07-02.md](file:///D:/AI-Workspace/projects/friday/docs/HERMES_RESTRUCTURE_2026-07-02.md))
2.  **การกำหนดไลบรารี:** สร้างไฟล์ [requirements.txt](file:///D:/AI-Workspace/projects/friday/requirements.txt) รวบรวมไลบรารีดักฟังเสียง เล่นเสียง และยิง API
3.  **การติดตั้ง Dependencies:** ติดตั้ง `pyaudio`, `SpeechRecognition` และ `pygame` ลงในสภาพแวดล้อม Python เรียบร้อยและทดสอบ import สำเร็จ
4.  **โค้ดสคริปต์หลัก:** สร้าง [friday_walkie_talkie.py](file:///D:/AI-Workspace/projects/friday/src/friday_walkie_talkie.py) ซึ่งเปลี่ยนบทบาทและเสียงเป็นเสียงผู้หญิงตามโปรไฟล์ของฟรายเดย์ (ใช้เสียง `th-TH-PremwadeeNeural`) 

---

## ขั้นตอนการทดสอบรันด้วยตัวเองในเครื่องคุณฟรี

เพื่อให้ระบบเปิดฟังเสียงจากไมโครโฟนจริงและพ่นเสียงออกลำโพงจริงของคุณฟรี ให้ทำตามขั้นตอนดังนี้ครับ:

1. เปิด **Terminal / PowerShell** ในเครื่องของคุณ
2. วิ่งไปที่โฟลเดอร์โครงการ:
   ```powershell
   cd D:\AI-Workspace\projects\friday
   ```
3. รันสคริปต์โดยใช้ Path ตัวแปลภาษาโดยตรงของ Conda ในเครื่อง (สคริปต์อยู่ใน `src/` หลัง Hermes จัดโครงสร้างใหม่ 2026-07-02):
   ```powershell
   C:\Users\Win10\miniconda3\envs\friday\python.exe src\friday_walkie_talkie.py
   ```
   (เดิมใช้ env `subtitle-aligner` ร่วมกับเครื่องมือตัดซับวิดีโอ — แยก env ใหม่ชื่อ `friday` ออกมาแล้วเมื่อ 2026-07-01 กันปัญหา dependency ชนกันในอนาคต ทั้งสอง env ไม่รบกวนกันแม้จะรันพร้อมกัน)
5.  **วิธีทดสอบคุย:**
    *   เมื่อหน้าจอขึ้นคำว่า `🎤 Friday: กำลังฟัง...` ให้ลองพูดคำถาม เช่น *"สวัสดีฟรายเดย์ วันนี้มีอะไรแนะนำบ้าง"*
    *   เงียบเสียงสักครู่ ระบบจะจับสัญญาณแล้วส่งไปประมวลผล จากนั้นจะพ่นเสียงภาษาไทยของฟรายเดย์ออกลำโพง
    *   หากต้องการปิดการทำงาน ให้พูดคำสั่งเสียงว่า *"ปิดเครื่อง"* หรือ *"จบการทำงาน"* เพื่อออกจากระบบอย่างสะอาด
