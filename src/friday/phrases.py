"""Fixed, safe phrase bank for short Friday responses.

These phrases are intentionally action-neutral. Dynamic tool confirmations must still include
the action/target in text before any confirm suffix is used.
"""

PHRASE_BANK = {
    "greeting": [
        {
            "id": "greeting_hello_short",
            "text": "สวัสดีค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "greeting_system_starting",
            "text": "ฟรายเดย์เริ่มระบบแล้วค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "greeting_back_online",
            "text": "กลับมาแล้วค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "greeting_need_help",
            "text": "สวัสดีค่ะนาย มีอะไรให้ช่วยคะ",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "12a727cddd1167a10a06a2e8c65840c8.wav",
        },
    ],
    "startup_status": [
        {
            "id": "startup_checking_mic_voice",
            "text": "ขอเช็คไมค์กับวอร์มเสียงแป๊บนึงค่ะ",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "startup_preparing_audio",
            "text": "กำลังเตรียมระบบเสียงให้พร้อมค่ะ",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "startup_calibrating",
            "text": "ขอปรับไมค์สั้นๆ ก่อนนะคะ",
            "safe_before_action": True,
            "requires_action_context": False,
        },
    ],
    "ready": [
        {
            "id": "ready_listening",
            "text": "พร้อมฟังค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "ready_system_ready",
            "text": "ระบบพร้อมแล้วค่ะ",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "ready_begin",
            "text": "เริ่มได้เลยค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "ready_mic_clear",
            "text": "ชัดเจนทุกคำค่ะ มีอะไรให้ช่วยไหมคะ",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "dcb13c6441f3d36c4c0bcf71dc3241ed.wav",
        },
    ],
    "ack": [
        {
            "id": "ack_understood",
            "text": "รับทราบค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "ack_ok",
            "text": "โอเคค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "ack_will_do",
            "text": "ได้เลยค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
    ],
    "wait_short": [
        {
            "id": "wait_one_moment",
            "text": "รอสักครู่นะคะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "wait_briefly",
            "text": "รอแป๊บนะคะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "wait_need_time",
            "text": "ขอเวลาสักครู่ค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
    ],
    "working": [
        {
            "id": "working_checking",
            "text": "กำลังเช็คให้อยู่ค่ะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "working_processing",
            "text": "ขอประมวลผลแป๊บนึงค่ะ",
            "safe_before_action": True,
            "requires_action_context": False,
        },
        {
            "id": "working_looking",
            "text": "กำลังดูให้นะคะ",
            "safe_before_action": True,
            "requires_action_context": False,
        },
    ],
    "signoff": [
        {
            "id": "signoff_rest_well",
            "text": "รับทราบค่ะ พักผ่อนให้เต็มที่นะคะนาย",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "a575090c2ecad98059621b544f98ccce.wav",
        },
    ],
    "clarification": [
        {
            "id": "clarify_close_target",
            "text": "ปิดโปรแกรมไหนคะ หรือจะให้ปิดระบบทั้งหมดเลยคะ",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "9ae38d46256d98f1b5577b57aa03b812.wav",
        },
    ],
    "tv_error": [
        {
            "id": "tv_error_wol_check",
            "text": "ทีวียังต่อไม่ติดค่ะ ลองเช็คปลั๊กหรือสัญญาณ Wake on LAN อีกทีนะคะ",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "863c1208d2f734f45e097523f45abee5.wav",
        },
        {
            "id": "tv_error_network_check",
            "text": "ดูเหมือนทีวีจะไม่ได้เปิดเครื่องหรือหลุดจากการเชื่อมต่อเครือข่ายค่ะ ลองเช็คปลั๊กหรือไวไฟดูนะคะ",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "8d040a0e57916ca90dbda7edb12476df.wav",
        },
        {
            "id": "tv_error_voice_ok",
            "text": "หมายถึงระบบรับเสียงทำงานปกติ แต่สั่งงานทีวีไม่ได้ใช่ไหมคะ",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "e1c8732b202fbc0fbfea51e6a92fb359.wav",
        },
        {
            "id": "tv_error_tool_unresponsive",
            "text": "เข้าใจแล้วค่ะ ระบบรับเสียงยังทำงานได้ดี แต่ตัวทีวีต่างหากที่ไม่ตอบสนองค่ะ",
            "safe_before_action": True,
            "requires_action_context": False,
            "source_cache_file": "a957eac82da05ee27c290cbedb530979.wav",
        },
    ],
    "confirm_suffix": [
        {
            "id": "confirm_suffix_confirm",
            "text": "ยืนยันไหมคะนาย",
            "safe_before_action": False,
            "requires_action_context": True,
        },
        {
            "id": "confirm_suffix_ok",
            "text": "ตกลงใช่ไหมคะนาย",
            "safe_before_action": False,
            "requires_action_context": True,
        },
        {
            "id": "confirm_suffix_confirm_thai",
            "text": "คอนเฟิร์มไหมคะนาย",
            "safe_before_action": False,
            "requires_action_context": True,
        },
    ],
}


def iter_phrases():
    for category, phrases in PHRASE_BANK.items():
        for phrase in phrases:
            yield category, phrase


def get_phrase(category, phrase_id=None):
    phrases = PHRASE_BANK[category]
    if phrase_id is None:
        return phrases[0]
    for phrase in phrases:
        if phrase["id"] == phrase_id:
            return phrase
    raise KeyError(f"unknown phrase_id for {category}: {phrase_id}")
