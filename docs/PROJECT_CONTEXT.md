# Project Context: Friday AI Assistant

**Last Updated:** 2026-07-01 10:50  
**Current Phase:** Phase 2 (Connecting with Local Tools & Agents)  
**Progress:** 30%  
**Next Session:** ดำเนินการเขียนตัวประมวลผลคำสั่งทูล (Tool Parser) ใน Python และเชื่อมเข้ากล่องจดหมาย Hermes Mailbox

---

## 🎯 สถานะปัจจุบัน

### เสร็จแล้ว (Completed)
| Phase | Tasks | เสร็จเมื่อ | หมายเหตุ |
|-------|-------|-----------|----------|
| Phase 1 | บิ้วด์โครงฐานเสียงโต้ตอบ Walkie-Talkie สำเร็จ | 2026-07-01 | คุยตอบโต้ได้จริง, ไม่เก็บขยะ, เสียงผู้หญิงนุ่มนวล |
| Phase 1 | แก้ปัญหาอ่านอิโมจิ & ปัญหาตัดเสียงพูดไวเกินไป | 2026-07-01 | เพิ่มฟังก์ชันตัดอิโมจิและเพิ่ม `pause_threshold = 1.5` |
| Phase 1 | ปรับปรุงความเร็ว Ollama & ความเสถียร TTS | 2026-07-01 | จำกัดบริบทโมเดลให้รันบน GPU 100% และย้ายคาลิเบรตไมค์ไปที่ Startup |
| Phase 1 | สลับไปใช้โมเดลคลาวด์ตัวเก่ง และระบบปิดตัวเองอัตโนมัติ | 2026-07-01 | ใช้โมเดล `gemma4:31b-cloud` และเพิ่มรหัสสั่งปิดตัว `[SHUTDOWN]` |

### กำลังทำ (In Progress)
| Phase | Tasks | เริ่มเมื่อ | คาดว่าเสร็จ |
|-------|-------|----------|-------------|
| Phase 2 | ออกแบบ Tool Parser คอยดักข้อความ เช่น `[TOOL: ...]` จากคำตอบ | 2026-07-01 | 2026-07-02 |
| Phase 2 | เชื่อมโยงระบบส่งงานเข้ากล่องจดหมาย Hermes Mailbox v2 | 2026-07-01 | 2026-07-02 |

### ยังไม่ได้ทำ (Pending)
| Phase | Tasks | Priority | Depends On |
|-------|-------|----------|------------|
| Phase 3 | อัปเกรดเป็นโหมดแยกรันขัดจังหวะได้ (Interruptible) | High | Phase 2 |
| Phase 4 | ออฟไลน์ 100% ด้วย Faster-Whisper ในเครื่อง | Medium | Phase 3 |

---

## 📝 Last Session Summary

**Session Date:** 2026-07-01  
**Model Used:** gemma4:31b-cloud (ผ่าน Local Ollama)

### ทำอะไรเสร็จไปบ้าง
- ✅ เปลี่ยนบทบาทผู้ช่วยและเสียงเป็น **ฟรายเดย์ (Friday)** เสียงผู้หญิงไทยของระบบคลาวด์ไมโครซอฟท์เสร็จสมบูรณ์
- ✅ แก้ปัญหาระบบดักฟังตัดคำพูดไวเกินไป และปรับระบบไมโครโฟนให้อิงตาม Default ของ Windows โดยอัตโนมัติ
- ✅ เพิ่มระบบสู้ชีวิต Retry Loop ให้กับการเรียก API คอนเนกชัน ทั้งของฝั่ง Ollama และ Edge-TTS ทำให้ระบบคุยได้ต่อเนื่องไม่เด้งหลุด
- ✅ แก้ปัญหาโมเดล Local กินแรมการ์ดจอล้นจนย้ายไปประมวลผลบน CPU ช้าค้างหน่วง โดยจำกัด `num_ctx: 2048` และสลับใช้ `gemma4:31b-cloud` คุยลื่นมากระดับวิจัยคำตอบได้ใน 1.5 วินาที
- ✅ พัฒนาให้เอไอสามารถคิดและส่งคำสั่งเพื่อปิดตัวเองได้จริง ด้วยการสังเกตคำสั่งปิดผ่านเสียง และส่งแท็กพิเศษ `[SHUTDOWN]` มาสั่งหยุดรันลูปออโต้

### เจอปัญหาอะไร
- ⚠️ **ปัญหา Edge-TTS Retry Error:** เกิดข้อความ `stream can only be called once` เมื่อพยายามลองใหม่ (Retry)
  - **วิธีแก้:** แก้ไขโค้ดให้สร้างวัตถุ `edge_tts.Communicate` ขึ้นมาใหม่ทุกรอบที่เข้ารูปแบบ Retry แทนการใช้วัตถุเดิมซ้ำ
- ⚠️ **ปัญหา Friday จำลองสั่งงานปลอม:** คุยตอบตกลงว่าจะส่งข้อความหา Hermes ใน Telegram ทั้งที่ยังไม่มีการเชื่อมทูลจริงๆ
  - **วิธีแก้:** บังคับในระบบ Prompt แจ้งความจริงว่าทูลสั่งการภายนอกยังไม่พร้อมในเฟสนี้ และสั่งให้ปฏิเสธการจำลองส่งสารอย่างเด็ดขาด

---

## 🚀 Next Steps

### ต้องทำอะไรต่อ (ลำดับความสำคัญ)
1. **High Priority:**
   - [ ] ออกแบบและเขียนทูลพาร์สเซอร์สำหรับ Friday เพื่ออ่านและรันคำสั่งพิเศษ
   - [ ] เขียนโค้ดส่วนเขียนไฟล์ Task JSON v2 ส่งเข้ากล่องจดหมาย `D:\AI-Workspace\mailbox\inbox\hermes\`
2. **Medium Priority:**
   - [ ] เพิ่มคำสั่งดึงสถานะพื้นฐานคอมพิวเตอร์ของคุณฟรี (เช่น แบตเตอรี่, เวลาปัจจุบัน, เปิดเบราว์เซอร์)
3. **Low Priority:**
   - [ ] ทดสอบความถูกต้องในการคุยโต้ตอบแล้วสั่งระบบสืบค้นงานจริง

---

## ❓ Open Questions / Decisions Needed

| คำถาม | ต้องตัดสินใจเมื่อ | Impact |
|-------|------------------|--------|
| พี่ต้องการให้รูปแบบคำสั่งที่ส่งไปให้ Hermes ทำงาน ใช้รูปแบบ JSON Task v2 แบบดั้งเดิมเลยใช่ไหม? | เริ่ม Phase 2 | รูปแบบโครงสร้างการอ่านเขียนไฟล์ในโฟลเดอร์ Mailbox |

---

## 📁 ไฟล์สำคัญในโปรเจค

| ไฟล์ | Path | หน้าที่ |
|------|------|--------|
| **PRD.md** | `D:\AI-Workspace\projects\friday\docs\PRD.md` | MASTER_BLUEPRINT ของโปรเจค |
| **PROJECT_CONTEXT.md** | `D:\AI-Workspace\projects\friday\docs\PROJECT_CONTEXT.md` | ข้อมูลอัปเดตและ Roadmap ปัจจุบัน |
| **WALKTHROUGH.md** | `D:\AI-Workspace\projects\friday\docs\WALKTHROUGH.md` | คู่มือรันระบบและการตั้งค่าเสียงเบื้องต้น |
| **FRIDAY_UI_DESIGN.md** | `D:\AI-Workspace\projects\friday\docs\FRIDAY_UI_DESIGN.md` | เอกสารการออกแบบ UI/UX โฮโลกราฟิกสะท้อนแสง |
| **Friday Script** | `D:\AI-Workspace\projects\friday\src\friday_walkie_talkie.py` | ไฟล์ทำงานหลัก (ย้ายเข้า `src/` โดย Hermes 2026-07-02) |

---

## 📊 Progress Timeline

```
Phase 1 (Dialogue Foundation)  : ████████████████████ 100%
Phase 2 (Mailbox & Tool Integration) : ██████░░░░░░░░░░░░░░░░░░  30%
Phase 3 (Interruptible Live VAD)     : ░░░░░░░░░░░░░░░░░░░░░░░░   0%
Phase 4 (100% Offline STT/TTS)       : ░░░░░░░░░░░░░░░░░░░░░░░░   0%
```

---

## 📞 Contact & Roles

| บทบาท | ใคร | ติดต่อ |
|-------|-----|--------|
| CEO / Project Owner | คุณฟรี | ในระบบ |
| Orchestrator / AI Assistant | Antigravity | ในระบบ |
| Local Worker Agent | Hermes | เครื่องคอมพิวเตอร์ |
| System Worker | OpenClaw | เครื่องคอมพิวเตอร์ |

---

**Template Version:** 1.0  
**Last Edited By:** Antigravity
