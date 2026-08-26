import ipaddress
import os
import re


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


def _env_str(name, default=""):
    return os.environ.get(name, default).strip()


def _env_optional_int(name, default=None):
    raw = _env_str(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _env_positive_float(name, default):
    raw = _env_str(name)
    if not raw:
        return float(default)
    try:
        value = float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero")
    return value


SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(SRC_DIR)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma4:31b-cloud"
# STT credential path is machine-local. No repository default: if unset/unavailable,
# _recognize_speech() falls back to the existing recognize_google() path instead of exposing
# a workstation-specific credential location in source.
GOOGLE_CLOUD_CREDS_PATH = _env_str("GOOGLE_CLOUD_CREDS_PATH")
TEMP_AUDIO_FILE = "friday_temp_response.mp3"
TEMP_AUDIO_FILE_FALLBACK = "friday_temp_response_fallback.wav"
VOICE_NAME = "th-TH-PremwadeeNeural"
JARVIS_VOICE = "th-TH-NiwatNeural"
SLOW_WARNING_MESSAGE = "ผมจาวิส รายงานครับ ไฟรเดย์กำลังเจอปัญหา รอสักครู่ครับนาย"
DEVICE_INDEX = _env_optional_int("FRIDAY_DEVICE_INDEX", None)
CAMERA_INDEX = _env_optional_int("FRIDAY_CAMERA_INDEX", 0)

# LG webOS TV configuration is machine-local. The old repository contained a paired client
# key in public source; all values now come from .env/process environment only. Re-pair the TV
# and rotate the old key before enabling control again.
TV_IP = _env_str("FRIDAY_TV_IP")
TV_MAC = _env_str("FRIDAY_TV_MAC")
TV_CLIENT_KEY = _env_str("FRIDAY_TV_CLIENT_KEY")
TV_CONNECT_TIMEOUT = _env_positive_float("FRIDAY_TV_CONNECT_TIMEOUT", 5)
TV_BROADCAST_IP = _env_str("FRIDAY_TV_BROADCAST_IP")
TV_BOOT_WAIT = _env_positive_float("FRIDAY_TV_BOOT_WAIT", 8)

_TV_MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


def tv_config_issues():
    """Return safe, value-free diagnostics for the optional LG TV integration."""
    required = {
        "FRIDAY_TV_IP": TV_IP,
        "FRIDAY_TV_MAC": TV_MAC,
        "FRIDAY_TV_CLIENT_KEY": TV_CLIENT_KEY,
        "FRIDAY_TV_BROADCAST_IP": TV_BROADCAST_IP,
    }
    missing = [name for name, value in required.items() if not value]
    issues = []
    if missing:
        issues.append("LG TV integration disabled: missing " + ", ".join(missing))
        return issues

    try:
        ipaddress.ip_address(TV_IP)
    except ValueError:
        issues.append("LG TV integration disabled: FRIDAY_TV_IP is not a valid IP address")
    try:
        ipaddress.ip_address(TV_BROADCAST_IP)
    except ValueError:
        issues.append("LG TV integration disabled: FRIDAY_TV_BROADCAST_IP is not a valid IP address")
    if not _TV_MAC_RE.fullmatch(TV_MAC):
        issues.append("LG TV integration disabled: FRIDAY_TV_MAC must use XX:XX:XX:XX:XX:XX format")
    return issues


def runtime_config_warnings():
    """Startup diagnostics. Messages intentionally contain variable names, never secret values."""
    warnings = []
    if not GOOGLE_CLOUD_CREDS_PATH:
        warnings.append("GOOGLE_CLOUD_CREDS_PATH is not set; Google Cloud STT may fall back to recognize_google")
    warnings.extend(tv_config_issues())
    return warnings


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
HERMES_SHADOW_LOG_DIR = os.path.join(VAULT_DIR, "hermes_shadow")

FRIDAY_FOR_HERMES_MODE = os.environ.get("FRIDAY_FOR_HERMES_MODE", "off").strip().lower()
HERMES_DASHBOARD_URL = os.environ.get("HERMES_DASHBOARD_URL", "http://127.0.0.1:9119").strip().rstrip("/")
HERMES_KEEPALIVE_INTERVAL_SECONDS = float(os.environ.get("HERMES_KEEPALIVE_INTERVAL_SECONDS", "5"))
HERMES_SYNC_SOFT_DETACH_SECONDS = float(os.environ.get("HERMES_SYNC_SOFT_DETACH_SECONDS", "20"))
HERMES_SYNC_HARD_TIMEOUT_SECONDS = float(os.environ.get("HERMES_SYNC_HARD_TIMEOUT_SECONDS", "60"))
HERMES_CONNECT_TIMEOUT_SECONDS = float(os.environ.get("HERMES_CONNECT_TIMEOUT_SECONDS", "5"))
FRIDAY_CORRELATION_ID_PREFIX = os.environ.get("FRIDAY_CORRELATION_ID_PREFIX", "ffh").strip() or "ffh"
FRIDAY_HERMES_CONTEXT_BUDGET_TOKENS = int(os.environ.get("FRIDAY_HERMES_CONTEXT_BUDGET_TOKENS", "2000"))
FRIDAY_HERMES_CONTEXT_POLICY = os.environ.get("FRIDAY_HERMES_CONTEXT_POLICY", "minimal").strip() or "minimal"

FIRE_REMINDER_SCRIPT = os.path.join(SRC_DIR, "fire_reminder.py")
