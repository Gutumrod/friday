"""ponytail: standalone entry point Task Scheduler runs to fire a set_timer reminder that
outlived Friday's process. Invoked as: pythonw.exe fire_reminder.py <message_b64> <task_name>
See _schedule_reminder_task() in friday_walkie_talkie.py for how this gets registered."""
import sys
import os
import subprocess
import base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import friday_walkie_talkie as fw


def main():
    message = base64.b64decode(sys.argv[1]).decode("utf-8")
    task_name = sys.argv[2]
    fw.speak(message)
    fw.log_to_vault("assistant", message)
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], capture_output=True)


if __name__ == "__main__":
    main()
