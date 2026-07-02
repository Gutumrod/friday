# Friday HUD UI Design Specifications (Golden Edition)

นี่คือแนวคิดการออกแบบหน้าจอหน้ากากผู้ใช้งาน (User Interface) ของ **Friday** ในสไตล์ HUD (Heads-Up Display) สีเหลืองทองล้ำยุค สไตล์ชุดเกราะไอรอนแมนของ Tony Stark เพื่อยกระดับความพรีเมียมจากสคริปต์คอมมานด์ไลน์ธรรมดาให้เป็นแอปพลิเคชันเดสก์ท็อปสุดหรูครับ

---

## 🎨 ภาพจำลองการออกแบบ (Mockup Design)

![Friday Golden HUD UI Mockup](file:///C:/Users/Win10/.gemini/antigravity/brain/aeda2b71-4420-48a7-9503-354017d85bea/friday_gold_ui_1782906121855.png)

---

## 📐 รายละเอียดองค์ประกอบการออกแบบ (UX/UI Spec)

การออกแบบนี้ยึดหลัก **"สีทอง ดุดัน และแสดงข้อมูลแบบเรียลไทม์" (Futuristic Golden HUD)** โดยอิงการเชื่อมต่อกับเครื่องมือและสคริปต์ของ Friday ที่มีอยู่ในปัจจุบัน:

### 1. The Core (ใจกลางระบบออดิโออัจฉริยะ)
*   **รูปทรง:** โฮโลกราฟิกรูปทรงกลม 3D สีทองสว่าง (Abstract Golden Energy Orb) ที่เคลื่อนไหวตามคลื่นเสียง
*   **สถานะสี:**
    *   **สีทองเหลืองอำพันหรี่ (Dim Amber Glow):** เมื่อสแตนด์บายรอฟื้นฟูระบบ (Idle)
    *   **สีส้มเพลิงพัลส์ (Pulsing Fire Orange):** ขณะที่เปิดไมโครโฟนตั้งใจดักฟังเสียงนาย (`mic_listening`)
    *   **สีเหลืองทองหมวนวน (Rotating Golden Yellow):** ขณะประมวลผลถามสมอง Ollama (`gemma4:31b-cloud`)
    *   **สีเหลืองอำพันกระพริบ (Flashing Amber):** ขณะเปล่งเสียงพูดออกลำโพง (`speak`)

### 2. Left Panel: System Telemetry & Memory (ฝั่งวินิจฉัยและหน่วยความจำ)
*   **System Diagnostics Widget:** แสดงกราฟและเปอร์เซ็นต์การใช้งาน CPU, RAM (ลิงก์กับเครื่องมือ `system_status` และ `list_processes`) และพื้นที่ว่างของฮาร์ดดิสก์ (`disk_space`) ในโทนเส้นใยสีเหลืองทองนีออน
*   **Memory Vault Cards:** แสดงข้อมูลสั้นๆ ที่ Friday ดึงมาจาก `vault/facts.md` เช่น โหมดเสียงที่เปิดใช้, ชื่อที่เรียกนาย, และกฎความปลอดภัยในปัจจุบัน

### 3. Right Panel: Active Session Log (ประวัติการสื่อสารปัจจุบัน)
*   **Chat Console:** บล็อกโปร่งแสงกรอบทองนีออน (Glassmorphic Container with Gold Neon Borders) แสดงข้อความสนทนาโต้ตอบระหว่างนายกับ Friday ใน Session ปัจจุบัน (ดึงข้อมูลเรียลไทม์จากไฟล์ `{date}_session-{NN}.md`)
*   **Command Bar (ล่างสุด):** ช่องพิมพ์ข้อความสำรองแบบกึ่งโปร่งแสง สำหรับพิมพ์ป้อนคำสั่งกรณีไม่สะดวกใช้เสียงคุย

### 4. Bottom Panel: Utility Dashboard (แถบควบคุมล่างสุด)
*   **Media Controller:** วิดเจ็ตขนาดเล็กควบคุมการเล่นเพลง ลิงก์ตรงกับทูล `media_control` (แสดงเพลงที่กำลังเล่น/ปุ่มกดข้ามเพลง)
*   **Timer Status:** แสดงเวลานับถอยหลังของ Reminders ที่ตั้งไว้จากทูล `set_timer`
*   **Clipboard Viewer:** แสดงข้อความที่พึ่งคัดลอกล่าสุดในบอร์ดที่ Friday ดึงมาจากทูล `clipboard_read`

---

## 🛠️ แนวทางพัฒนาหน้าจอนี้ในอนาคต

เราสามารถสร้างหน้าจอนี้ให้เกิดขึ้นจริงได้โดยไม่รบกวนโครงสร้าง Python คอร์หลักของ Friday ด้วยวิธีการดังนี้ครับ:
1.  **WebView / Local Web Tech (แนะนำ):** พัฒนาหน้าจอด้วย HTML5 / CSS3 (Vanilla CSS + CSS Animations สำหรับคลื่นเสียง 3D) และ Javascript
2.  **WebSocket Connection:** ให้สคริปต์ Python (`friday_walkie_talkie.py`) เปิดเซิร์ฟเวอร์ WebSocket สื่อสารระยะสั้นในเครื่อง เมื่อสคริปต์เปลี่ยนสถานะ (เช่น เริ่มดักฟัง, ได้คำตอบ, หรือรัน Tool) จะยิงสถานะไปเปลี่ยนอนิเมชั่นของเว็บเพจหน้าจอนี้ทันที
3.  **Desktop Overlay:** สามารถปล่อยรันแบบโปร่งแสง ไร้กรอบขอบหน้าต่าง (Borderless Windows) แปะไว้มุมใดมุมหนึ่งของหน้าจอเดสก์ท็อปของคุณฟรีได้อย่างสวยงาม
