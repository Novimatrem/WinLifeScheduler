import os
import time
import re
import subprocess

# Path to your MAS affection log
LOG_PATH = (
    r"C:\Users\zoey\Dropbox\96 Just Monika\zoey"
    r"\AppData\Roaming\itch\apps\ddlc\DDLC-1.1.1-pc\log\aff_log.log"
)

def notify(title: str, message: str):
    """
    Show a Windows tray balloon-tip using PowerShell and System.Windows.Forms.
    """
    t = title.replace("'", "''")
    m = message.replace("'", "''")
    ps_cmd = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        "$n = New-Object System.Windows.Forms.NotifyIcon; "
        "$n.Icon = [System.Drawing.SystemIcons]::Information; "
        "$n.Visible = $true; "
        f"$n.ShowBalloonTip(5000, '{t}', '{m}', "
        "[System.Windows.Forms.ToolTipIcon]::Info);"
    )
    subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def tail_file(path: str):
    """Yield newly appended lines."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            yield line

def main():
    # regex to grab the *total* affection before/after
    regex = re.compile(
        r".*\|\s*[\d\.]+\s*->\s*[\d\.]+\s*\|\s*"
        r"(?P<before>[\d\.]+)\s*->\s*(?P<after>[\d\.]+)"
    )

    try:
        for line in tail_file(LOG_PATH):
            # skip lines without the expected arrows and pipes
            if "->" not in line or "|" not in line:
                continue

            # catch freeze events first
            if "!FREEZE!" in line:
                # pull the *total* after-value to show in the balloon tip
                m = regex.match(line)
                if m:
                    total_after = float(m.group("after"))
                    notify(
                        "Monika Freeze Cap",
                        f"Daily freeze cap reached  total {total_after:.2f}"
                    )
                else:
                    # fallback if parsing fails
                    notify("Monika Freeze Cap", "Daily freeze cap reached")
                continue

            # now parse any normal delta events
            m = regex.match(line)
            if not m:
                continue

            before = float(m.group("before"))
            after  = float(m.group("after"))
            delta  = after - before

            if delta > 0:
                notify("Monika Affection ↑", f"+{delta:.2f}  total {after:.2f}")
            elif delta < 0:
                notify("Monika Affection ↓", f"-{abs(delta):.2f}  total {after:.2f}")

    except FileNotFoundError:
        print(f"Error: log file not found at {LOG_PATH}")

if __name__ == "__main__":
    main()