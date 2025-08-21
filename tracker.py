import time
import pandas as pd
import datetime
from pathlib import Path
import pygetwindow as gw

LOG_FILE = "usage_log.csv"
SAMPLE_SECONDS = 15  # keep in sync with analyze.py

def get_active_window_title():
    """Return the current active window title (best-effort)."""
    try:
        win = gw.getActiveWindow()
        if win is None:
            return "Unknown"
        title = (win.title or "Unknown").strip()
        # Normalize very long titles
        return title[:200] if title else "Unknown"
    except Exception:
        return "Unknown"

def log_usage():
    print("📊 Tracking started... Press Ctrl+C to stop.")
    header_needed = not Path(LOG_FILE).exists()
    # Write header once
    if header_needed:
        pd.DataFrame(columns=["timestamp", "app"]).to_csv(LOG_FILE, index=False)

    while True:
        app_title = get_active_window_title()
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Append row directly to CSV without full dataframe overhead
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{ts},{app_title.replace(',', ' ')}\n")
        time.sleep(SAMPLE_SECONDS)

if __name__ == "__main__":
    try:
        log_usage()
    except KeyboardInterrupt:
        print("\n🛑 Stopped tracking.")
