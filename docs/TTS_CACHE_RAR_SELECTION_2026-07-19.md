# TTS Cache RAR Selection

วันที่: 2026-07-19
source archive: `D:\AI-Workspace\projects\friday\src\tts_cache\tts_cache.rar`

ไฟล์ใน archive เป็น JaiTTS `.wav` cache แบบ hash เดิม 27 ไฟล์ ไม่มี manifest เดิมแนบมา จึง reverse-map ด้วย `md5(VOICE_NAME:text)` จากประโยคใน repo/vault และถอด STT เพิ่ม 1 ไฟล์ที่ไม่ match

## Promote Candidates

ไฟล์กลุ่มนี้เหมาะเอาไปตั้งชื่อใหม่/เพิ่มเป็น phrase variant หรือใช้ใน flow เฉพาะทาง

| File | Text | Suggested use |
|---|---|---|
| `12a727cddd1167a10a06a2e8c65840c8.wav` | สวัสดีค่ะนาย มีอะไรให้ช่วยคะ | `greeting` variant |
| `dcb13c6441f3d36c4c0bcf71dc3241ed.wav` | ชัดเจนทุกคำค่ะ มีอะไรให้ช่วยไหมคะ | `ready` / mic-check success |
| `a575090c2ecad98059621b544f98ccce.wav` | รับทราบค่ะ พักผ่อนให้เต็มที่นะคะนาย | shutdown / signoff |
| `9ae38d46256d98f1b5577b57aa03b812.wav` | ปิดโปรแกรมไหนคะ หรือจะให้ปิดระบบทั้งหมดเลยคะ | close-action clarification |
| `863c1208d2f734f45e097523f45abee5.wav` | ทีวียังต่อไม่ติดค่ะ ลองเช็คปลั๊กหรือสัญญาณ Wake on LAN อีกทีนะคะ | TV connection failure |
| `8d040a0e57916ca90dbda7edb12476df.wav` | ดูเหมือนทีวีจะไม่ได้เปิดเครื่องหรือหลุดจากการเชื่อมต่อเครือข่ายค่ะ ลองเช็คปลั๊กหรือไวไฟดูนะคะ | TV network failure |
| `dfd88e197a2e8c98c67b23d66fe080a7.wav` | ต่อทีวีไม่ได้ค่ะ: [WinError 10060] A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond | TV timeout debug, not casual voice |
| `e1c8732b202fbc0fbfea51e6a92fb359.wav` | หมายถึงระบบรับเสียงทำงานปกติ แต่สั่งงานทีวีไม่ได้ใช่ไหมคะ | TV troubleshooting clarification |
| `a957eac82da05ee27c290cbedb530979.wav` | เข้าใจแล้วค่ะ ระบบรับเสียงยังทำงานได้ดี แต่ตัวทีวีต่างหากที่ไม่ตอบสนองค่ะ | TV troubleshooting summary |

## Keep As Cache Only

ใช้ซ้ำได้เฉพาะถ้า text เดิมตรงเป๊ะ แต่ไม่ควร promote เป็น phrase ทั่วไป เพราะมีค่าเวลา/สถานะ/target เฉพาะตอนนั้น

| File | Text | Reason |
|---|---|---|
| `0ebbffea87bcdfe51630549e38bf9b24.wav` | ตอนนี้เวลา 08:21 น. วันที่ 04/07/2026 ค่ะ | stale time |
| `9541170a97077671b0629d938bbc9900.wav` | ตอนนี้เวลา 08:43 น. วันที่ 04/07/2026 ค่ะ | stale time |
| `a99012bdb5e6a519a3ef0fa328060225.wav` | ตอนนี้เวลา 21:05 น. วันที่ 19/07/2026 ค่ะ | stale time |
| `b1e24e2b737fff011f0fa85d32ceef20.wav` | ตอนนี้เวลา 21:22 น. วันที่ 19/07/2026 ค่ะ | stale time |
| `da87c6e9635be95ed18e49e737f19c21.wav` | ตอนนี้เวลา 21:33 น. วันที่ 18/07/2026 ค่ะ | stale time |
| `487c04f0930a6d6e1474af494212de2d.wav` | ตอนนี้ CPU ใช้งานอยู่ 10% เครื่องเปิดมาแล้ว 37 ชั่วโมง 0 นาทีค่ะ อินเทอร์เน็ตต่อติดปกติค่ะ ดิสก์ C เหลือว่าง 74 GB จากทั้งหมด 465 GB ค่ะ | stale system status |
| `3d86f9a0546f3c2c526f4fff35227658.wav` | ต้องการค้นหา 'สภาพอากาศ กรุงเทพฯ ตอนนี้' นะคะ ยืนยันไหมคะ | exact dynamic confirm |
| `4db673bee3a2d78621d54395be22f28a.wav` | ได้ค่ะ ต้องการปิดทีวีนะคะ ยืนยันไหมคะ | exact TV confirm |
| `c1dd66912063947063256e6092509542.wav` | ได้ค่ะ จะให้เปิดในทีวีเลยนะคะ ต้องการเปิด 'The Ghost Radio' ในทีวีนะคะ ยืนยันไหมคะ | exact TV/YouTube confirm |
| `549ffe541d26fd72e93cf671a1f982d8.wav` | เปิด Chrome ให้หน่อยค่ะนายเดี๋ยวเช็ค YouTube ให้ด้วยนะคะ | exact old request wording |

## Do Not Promote

กลุ่มนี้ไม่ควรเอาเข้า phrase bank เพราะ specific เกินไป, stale, หรือมี error/raw output ที่ไม่เหมาะเป็นเสียงทั่วไป

| File | Text | Reason |
|---|---|---|
| `ab2b871f9ff410e1095149d2cd2c90b4.wav` | หาเพลง 'The Ghost Radio' ไม่เจอค่ะ: ERROR: [youtube] Ruw6cSdSkAk: Join this channel to get access to members-only content like this video, and other exclusive perks. | raw YouTube error, noisy |
| `3a6806cd574aace9aad9420ba3830c8b.wav` | ดูเหมือนทีวีจะไม่ตอบสนองต่อคำขอเชื่อมต่อค่ะ ให้เช็คสถานะเน็ตเวิร์กของเครื่องก่อนไหมคะ | useful, but overlaps better TV failure variants |
| `8a2358eab24a14c4f43d487f79d18d6b.wav` | ต้องขออภัยค่ะ นายยังไม่ได้สั่งให้ปิดเลยค่ะ จะให้ปิดตอนนี้เลยไหมคะ | confusing without context |
| `17b4fc5a1df21dca039aaa34d85b52f1.wav` | เข้าใจแล้วค่ะ สรุปคือเปลี่ยนระบบเสียงใหม่นะคะ | one-off conversation |
| `9097981f412d37933e2a9f317abd15fc.wav` | หมายถึงต้องการเปลี่ยนเสียงของฉัน หรือให้ช่วยปรับระดับเสียงเครื่องคะ | one-off clarification |
| `042de41d309665facbebbf1f15b024df.wav` | ภาษาไทยค่ะ นายหูฝาดหรือเปล่าคะ | too playful/specific |
| `62f0cde3dc80ebca5273939eb3d0e6bc.wav` | หูดีขึ้นหรือเปล่าคะ หรือว่าแค่เสียงฉันเปลี่ยนไปคะ | voice-test specific |
| `6fc522b0bb19d3fc86e2cf5c0eb51461.wav` | มีเครื่องมือจัดการระบบ เปิดแอป เว็บ ค้นหาข้อมูล ควบคุมสื่อและทีวี และส่งงานต่อให้ Hermes ค่ะ ต้องการให้ช่วยอะไรเป็นพิเศษไหมคะ | long capability explainer |

## Recommended Next Step

1. Promote only the first 5-7 files from `Promote Candidates` into named phrase IDs.
2. Keep TV error variants for the next TV/YouTube tool repair pass.
3. Do not reuse stale time/system-status audio even if the voice sounds good.
4. If any promoted audio is copied into `src/tts_cache/phrases/`, keep it runtime-only and regenerate/copy it on Mac instead of committing binary audio.

## Promoted On 2026-07-19

These files were copied from `tts_cache.rar` into runtime-only `src/tts_cache/phrases/` with stable phrase IDs:

| Phrase ID | Runtime audio file | Source hash file |
|---|---|---|
| `greeting_need_help` | `src/tts_cache/phrases/greeting_need_help.wav` | `12a727cddd1167a10a06a2e8c65840c8.wav` |
| `ready_mic_clear` | `src/tts_cache/phrases/ready_mic_clear.wav` | `dcb13c6441f3d36c4c0bcf71dc3241ed.wav` |
| `signoff_rest_well` | `src/tts_cache/phrases/signoff_rest_well.wav` | `a575090c2ecad98059621b544f98ccce.wav` |
| `clarify_close_target` | `src/tts_cache/phrases/clarify_close_target.wav` | `9ae38d46256d98f1b5577b57aa03b812.wav` |
| `tv_error_wol_check` | `src/tts_cache/phrases/tv_error_wol_check.wav` | `863c1208d2f734f45e097523f45abee5.wav` |
| `tv_error_network_check` | `src/tts_cache/phrases/tv_error_network_check.wav` | `8d040a0e57916ca90dbda7edb12476df.wav` |
| `tv_error_voice_ok` | `src/tts_cache/phrases/tv_error_voice_ok.wav` | `e1c8732b202fbc0fbfea51e6a92fb359.wav` |
| `tv_error_tool_unresponsive` | `src/tts_cache/phrases/tv_error_tool_unresponsive.wav` | `a957eac82da05ee27c290cbedb530979.wav` |
