# analyze.py
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

from pet_manager import load_zoo, record_new_pet, level_up_last_pet

LOG_FILE = "usage_log.csv"
SAMPLE_SECONDS = 15        # MUST match tracker.py sampling interval
ACTIVITY_FILE = "activity_dates.csv"

# Streak days that unlock a new pet
NEW_PET_STREAKS = {1, 2, 5, 10, 20, 30, 50, 100}
# Minutes per day that will level up the latest pet
LEVELUP_MINUTES = 90

def _mark_activity_today():
    today = datetime.now().date().strftime("%Y-%m-%d")
    if Path(ACTIVITY_FILE).exists():
        df = pd.read_csv(ACTIVITY_FILE)
    else:
        df = pd.DataFrame(columns=["date"])
    if today not in df["date"].astype(str).values:
        df.loc[len(df)] = [today]
        df.to_csv(ACTIVITY_FILE, index=False)

def _compute_streak():
    """Return number of consecutive days with activity ending today."""
    if not Path(ACTIVITY_FILE).exists():
        return 0
    df = pd.read_csv(ACTIVITY_FILE)
    if df.empty:
        return 0
    dates = sorted(pd.to_datetime(df["date"]).dt.date.tolist())
    streak = 0
    cur = datetime.now().date()
    while cur in dates:
        streak += 1
        cur = cur - timedelta(days=1)
    return streak

def analyze_today():
    if not Path(LOG_FILE).exists():
        print("No usage_log.csv found. Run tracker.py first and let it log some data.")
        return

    df = pd.read_csv(LOG_FILE)
    if df.empty:
        print("Log file is empty. Let tracker run longer.")
        return

    # Ensure timestamp column is datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    today = datetime.now().date()
    df_today = df[df["timestamp"].dt.date == today]

    if df_today.empty:
        print("No entries for today yet. Run tracker and try again later.")
        return

    total_minutes = len(df_today) * SAMPLE_SECONDS / 60.0

    # Per-window summary (for dashboard)
    counts = df_today["app"].value_counts().rename_axis("app").reset_index(name="samples")
    counts["minutes"] = counts["samples"] * SAMPLE_SECONDS / 60.0
    counts.sort_values("minutes", ascending=False).to_csv("daily_summary.csv", index=False)

    # Mark today's activity and compute streak
    _mark_activity_today()
    streak = _compute_streak()

    print(f"Today's minutes tracked: {total_minutes:.1f} | Current streak: {streak} day(s)")

    # Load zoo and apply milestones
    zoo = load_zoo()
    did = False

    # If first pet ever OR current streak matches a new-pet milestone -> unlock
    if zoo.empty or streak in NEW_PET_STREAKS:
        zoo, pet_type, level = record_new_pet(zoo)
        print(f"🎉 New pet unlocked: {pet_type} (Level {level}) — streak {streak}")
        did = True
    # Else if today we logged enough minutes -> level up last pet
    elif total_minutes >= LEVELUP_MINUTES:
        zoo, pet_type, level = level_up_last_pet(zoo)
        print(f"⬆️ Pet leveled up: {pet_type} (Level {level}) — {total_minutes:.0f} min today")
        did = True

    if not did:
        print("No new pet or level today — keep going!")

if __name__ == "__main__":
    analyze_today()
