import time

import requests


def ask_ollama(
    prompt,
    history,
    tools=None,
    *,
    model_name,
    ollama_url,
    speak_fn,
    slow_warning_message,
    jarvis_voice,
):
    """Send conversation history to local Ollama API with retry mechanism."""
    messages = history + [{"role": "user", "content": prompt}]
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "num_ctx": 16000  # ponytail: gemma4:31b-cloud รันบนคลาวด์ Ollama ไม่ใช่ GPU เครื่องนี้ รองรับ context ถึง 262144 จริง ค่านี้กันคุยยาวแล้วลืมบทก่อนหน้า ปรับเพิ่มได้ถ้ายังไม่พอ
        },
    }
    if tools:
        payload["tools"] = tools

    # Retry up to 3 times for cloud network resilience
    start = time.time()
    warned_slow = False
    for attempt in range(3):
        try:
            response = requests.post(ollama_url, json=payload, timeout=30)
            if response.status_code == 200:
                message = response.json()["message"]
                return {"content": message.get("content", ""), "tool_calls": message.get("tool_calls")}
            else:
                print(f"⚠️ Ollama API attempt {attempt+1} returned status code: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Ollama connection attempt {attempt+1} failed: {e}")
        # measured during stress testing: a single retry can silently eat 25-48s with the
        # user sitting in dead air -- speak up once so it doesn't feel like Friday hung
        if not warned_slow and time.time() - start > 25:
            warned_slow = True
            speak_fn(slow_warning_message, voice=jarvis_voice)
        time.sleep(1.5)

    return {"content": "ขออภัยด้วยค่ะนาย การเชื่อมต่อกับสมองหลักคลาวด์เกิดขัดข้องชั่วคราว ลองถามใหม่อีกครั้งได้ไหมคะ", "tool_calls": None}
