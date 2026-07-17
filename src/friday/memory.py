import os
import re
from datetime import datetime


SESSION_FILE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})_session-(\d+)\.md$")
LEGACY_DAY_FILE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")


def load_facts(facts_path):
    """Read Friday's long-term facts about นาย from the vault, if any."""
    if not os.path.exists(facts_path):
        return ""
    with open(facts_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL).strip()
    return content


def migrate_legacy_day_files(history_dir):
    """One-time migration from per-day files to per-session files."""
    if not os.path.isdir(history_dir):
        return []
    migrated = []
    for filename in os.listdir(history_dir):
        if not LEGACY_DAY_FILE_PATTERN.match(filename):
            continue
        date_part = filename[:-3]
        new_path = os.path.join(history_dir, f"{date_part}_session-01.md")
        if not os.path.exists(new_path):
            os.rename(os.path.join(history_dir, filename), new_path)
            migrated.append(filename)
    return migrated


def start_new_session(history_dir):
    """Start a new per-run history file, numbered per day: '{date}_session-{NN}.md'."""
    os.makedirs(history_dir, exist_ok=True)
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    existing_numbers = []
    for filename in os.listdir(history_dir):
        m = SESSION_FILE_PATTERN.match(filename)
        if m and m.group(1) == today:
            existing_numbers.append(int(m.group(2)))
    session_number = max(existing_numbers) + 1 if existing_numbers else 1
    path = os.path.join(history_dir, f"{today}_session-{session_number:02d}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"## Session {session_number} — เริ่ม {now.strftime('%H:%M:%S')}\n\n")
    return session_number, path


def log_to_vault(session_path, role, text):
    """Append a conversation turn to the current session's history file."""
    with open(session_path, "a", encoding="utf-8") as f:
        f.write(f"### {datetime.now().strftime('%H:%M:%S')} — {role}\n{text}\n\n")
