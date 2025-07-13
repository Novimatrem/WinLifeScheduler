import time
import datetime
import ctypes
import winsound
import threading

def clear_terminal():
    for _ in range(300):
        print()
        time.sleep(0.002)

# Set how many times the alert loop should run
ALERT_REPEAT_COUNT = 10

def show_popup(event_label):
    ctypes.windll.user32.MessageBoxW(
        0,
        f"{event_label} (Life Scheduler)",
        "⚠️ Life Scheduler Alert",
        0x40  # MB_ICONINFORMATION
    )

def run_alert(event_label):
    print(f"[ALERT] Event triggered — {event_label}")

    # Beep sequence from rumble to shriek
    blast_sequence = [
        400, 600, 800, 1000,
        1200, 1600, 2000,
        22000, 21000, 20000,
    ]

    # Main alert barrage
    for _ in range(ALERT_REPEAT_COUNT):
        for freq in blast_sequence:
            winsound.Beep(freq, 180)

    # Final sonic stab: alternating low-high slap
    for i in range(20):
        freq = 400 if i % 2 == 0 else 22000
        winsound.Beep(freq, 100)

    # Launch message box in separate thread (non-blocking)
    threading.Thread(target=show_popup, args=(event_label,), daemon=True).start()

def prevent_sleep():
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    result = ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )
    if result == 0:
        print("[WARN] Failed to set execution state.")

def check_event(now, day, hour, minute):
    return (
        now.strftime("%A") == day and
        now.hour == hour and
        now.minute == minute
    )

EVENTS = [
    ("Movement Group",     "Monday",     9, 55),
    ("Walking Group",      "Wednesday", 11, 55),
    ("Shower Reminder",    "Friday",    16, 3),
    ("Testing Event",      "Sunday",    12, 7),
    ("Testing Event 2",    "Sunday",    12, 9),
]

for weekday in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
    EVENTS.append(("Wake Up Reminder", weekday, 8, 30))
    EVENTS.append(("Sleep Reminder",   weekday, 0, 0))

def main():
    clear_terminal()
    print("Life Scheduler")
    print("Licensed under GNU GPL v3.0")
    print("https://www.gnu.org/licenses/gpl-3.0.en.html")

    # ⏰ Immediate alert test for wakefulness confirmation
    run_alert("Startup Diagnostic Completed")

    last_triggered = None

    while True:
        now = datetime.datetime.now()
        time_str = now.strftime('%A %H:%M')
        print(f"\n[TICK] {time_str}")
        prevent_sleep()

        for label, day, hour, minute in EVENTS:
            if check_event(now, day, hour, minute):
                current_id = f"{day}_{hour}_{minute}"
                if last_triggered != current_id:
                    run_alert(label)
                    last_triggered = current_id
                else:
                    print(f"[DEBUG] Skipping repeat alert for {label}.")
                break

        time.sleep(1)

if __name__ == "__main__":
    main()
