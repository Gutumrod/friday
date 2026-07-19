import os


def load_dotenv():
    """ponytail: stdlib-only .env loader -- not worth adding python-dotenv as a dependency for
    parsing a handful of KEY=VALUE lines."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


load_dotenv()

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(SRC_DIR)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:31b-cloud"
# STT: Google Cloud Speech-to-Text (official, paid-but-cheap) replaces the free/unofficial
# recognize_google() endpoint below -- 2026-07-04, see listen_mic(). Credentials borrowed from
# the existing craftbike_bot GCP project (CEO confirmed it's unused for anything else, API
# enabled on that project specifically for this).
GOOGLE_CLOUD_CREDS_PATH = os.environ.get("GOOGLE_CLOUD_CREDS_PATH", r"D:\craftbike_bot\credentials.json")
TEMP_AUDIO_FILE = "friday_temp_response.mp3"
TEMP_AUDIO_FILE_FALLBACK = "friday_temp_response_fallback.wav"
VOICE_NAME = "th-TH-PremwadeeNeural"  # Microsoft Premwadee (Thai Female - Friday)
JARVIS_VOICE = "th-TH-NiwatNeural"  # Microsoft Niwat (Thai Male) -- used only for the cloud-slow warning below, speak(voice=...)
SLOW_WARNING_MESSAGE = "ผมจาวิส รายงานครับ ไฟรเดย์กำลังเจอปัญหา รอสักครู่ครับนาย"
DEVICE_INDEX = None  # ใส่เลข Index ของไมค์ที่ใช้จริง (เช่น 4 สำหรับ HyperX, 1 สำหรับ Razer X) ถ้าเว้น None จะใช้ไมค์หลักของ Windows
CAMERA_INDEX = 0  # index ของกล้องเว็บแคมที่ใช้จริง (เครื่องนี้มีกล้องเดียว = Razer Kiyo = 0) เครื่องอื่นที่มีหลายตัวอาจไม่ใช่ 0 เช็คด้วย Get-PnpDevice -Class Camera ก่อนเปลี่ยน

# LG webOS TV (2026-07-03 live test, see notes/lg-tv-control-live-test-2026-07-03.md) -- ค่าพวกนี้
# เฉพาะเครื่องนี้ทั้งหมด เปลี่ยนตามบ้าน/ทีวีจริงถ้าเอาไปใช้เครื่องอื่น
TV_IP = "192.168.1.107"
TV_MAC = "58:fd:b1:dc:44:c3"
TV_CLIENT_KEY = "974cfe0f19cc5c3ac719b2e3726ffcaf"
TV_CONNECT_TIMEOUT = 5
TV_BROADCAST_IP = "192.168.1.255"
TV_BOOT_WAIT = 8

# dispatch_to_hermes -- see docs/../shared/decisions/dispatch-to-hermes-contract-2026-07-02.md
MAILBOX_DIR = r"D:\AI-Workspace\mailbox"
DISPATCH_TO_HERMES_TIMEOUT = 300
DISPATCH_TO_HERMES_POLL_INTERVAL = 3
# n8n "FRIDAY Mailbox Notifier" -- see docs/N8N_MAILBOX_NOTIFIER_2026-07-03.md
MAILBOX_INBOX_HERMES_DIR = os.path.join(MAILBOX_DIR, "inbox", "hermes")

TTS_CACHE_DIR = os.path.join(SRC_DIR, "tts_cache")
PHRASE_AUDIO_DIR = os.path.join(TTS_CACHE_DIR, "phrases")

JAITTS_REPO = "JTS-AI/JaiTTS-F5TTS"
VOICES_DIR = os.path.join(PROJECT_DIR, "voices")
JAITTS_REF_AUDIO = os.path.join(VOICES_DIR, "jaitts_reference.wav")
JAITTS_REF_TEXT = (
    "สวัสดีค่ะนาย Friday พร้อมรับคำสั่งแล้วค่ะ ตอนนี้กำลังทดสอบระบบ voice cloning อยู่ค่ะ "
    "มีอะไรให้ Friday รับใช้ นายบอกได้เลยนะคะ Friday พร้อมทำงานแล้วค่ะ"
)

VAULT_DIR = os.path.join(PROJECT_DIR, "vault")
FACTS_PATH = os.path.join(VAULT_DIR, "facts.md")
HISTORY_DIR = os.path.join(VAULT_DIR, "history")
LATENCY_LOG_DIR = os.path.join(VAULT_DIR, "latency")

FIRE_REMINDER_SCRIPT = os.path.join(SRC_DIR, "fire_reminder.py")
