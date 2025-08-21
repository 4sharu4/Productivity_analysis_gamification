from datetime import datetime, timedelta
import pandas as pd
import os

from pet_manager import load_zoo, record_new_pet, update_pets

# ---------- Config ----------
LOG_FILE = "usage_log.csv"
DAILY_HISTORY = "daily_history.csv"
ACTIVITY_FILE = "activity_dates.csv"
ACCUMULATION_FILE = "accumulated_minutes.csv"
DEBUG_OTHER = "uncategorized_log.txt"

SAMPLE_SECONDS = 15
NEW_PET_STREAKS = {1, 2, 5, 10, 15, 20, 30, 50, 100}

PRODUCTIVITY = {
    "vs code": "Good", "email": "Good", "docs": "Good",
    "notepad": "Neutral", "youtube": "Bad", "netflix": "Bad",
    "games": "Bad", "other": "Neutral",
    "power bi": "Good", "explorer": "Neutral"
}

# ---------- Utility Functions ----------
def clean_app_name(name):
    name = str(name).lower()

    if "youtube" in name:
        return "YouTube"
    elif "chrome" in name:
        return "Chrome"
    elif "vs code" in name or "visual studio" in name:
        return "VS Code"
    elif "mail" in name or "outlook" in name:
        return "Email"
    elif "microsoft to do" in name:
        return "microsoft_to_do"
    elif "netflix" in name:
        return "Netflix"
    elif "notepad" in name:
        return "Notepad"
    elif "productivity_analysis_gamification" in name:
        return "Github"
    elif "game" in name:
        return "Games"
    elif "bitrial" in name:
        return "Power BI"
    elif "explorer" in name or "this pc" in name or "folder" in name:
        return "Explorer"
    else:
        with open(DEBUG_OTHER, "a", encoding="utf-8") as f:
            f.write(name + "\n")
        return "Other"

def mark_activity_today():
    today = datetime.now().date().strftime("%Y-%m-%d")
    if os.path.exists(ACTIVITY_FILE):
        df = pd.read_csv(ACTIVITY_FILE)
    else:
        df = pd.DataFrame(columns=["date"])
    if today not in df["date"].astype(str).values:
        df.loc[len(df)] = [today]
        df.to_csv(ACTIVITY_FILE, index=False)

def compute_streak():
    if not os.path.exists(ACTIVITY_FILE):
        return 0
    df = pd.read_csv(ACTIVITY_FILE)
    dates = sorted(pd.to_datetime(df["date"]).dt.date.tolist())
    streak = 0
    cur = datetime.now().date()
    while cur in dates:
        streak += 1
        cur -= timedelta(days=1)
    return streak

# ---------- Main Analysis ----------
def analyze_today():
    if not os.path.exists(LOG_FILE):
        print("No usage_log.csv found.")
        return

    df = pd.read_csv(LOG_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df["app"] = df["app"].apply(clean_app_name)

    today = datetime.now().date()
    df_today = df[df["timestamp"].dt.date == today]
    if df_today.empty:
        print("No usage data for today.")
        return

    total_samples = len(df_today)
    total_minutes = total_samples * SAMPLE_SECONDS / 60.0

    # Build summary dataframe
    summary = df_today["app"].value_counts().rename_axis("app").reset_index(name="samples")
    summary["minutes"] = summary["samples"] * SAMPLE_SECONDS / 60.0
    summary["productivity"] = summary["app"].apply(lambda x: PRODUCTIVITY.get(x.lower(), "Neutral"))
    summary["date"] = str(today)

    # Append to daily history (overwrite existing entry for today if exists)
    if os.path.exists(DAILY_HISTORY):
        history_df = pd.read_csv(DAILY_HISTORY)
        history_df = history_df[history_df["date"] != str(today)]
        history_df = pd.concat([history_df, summary], ignore_index=True)
    else:
        history_df = summary
    history_df.to_csv(DAILY_HISTORY, index=False)

    # Save to accumulation file
    if os.path.exists(ACCUMULATION_FILE):
        acc_df = pd.read_csv(ACCUMULATION_FILE)
        acc_df = acc_df[acc_df["date"] != str(today)]  # Prevent duplicates
    else:
        acc_df = pd.DataFrame(columns=["date", "minutes"])
    acc_df.loc[len(acc_df)] = [str(today), total_minutes]
    acc_df.to_csv(ACCUMULATION_FILE, index=False)

    # Update activity log
    mark_activity_today()
    streak = compute_streak()
    print(f"Tracked {total_minutes:.1f} minutes today — streak: {streak} day(s)")

    # ---------- Pet Evolution ----------
    zoo = load_zoo()
    today_str = str(today)
    pet_created_today = not zoo.empty and zoo["start_date"].astype(str).eq(today_str).any()

    if zoo.empty or (streak in NEW_PET_STREAKS and not pet_created_today):
        zoo, pet_type, lvl = record_new_pet(zoo)
        print(f"🎉 New pet unlocked: {pet_type} (Level {lvl})")
        # Also update pets to add minutes for today on creation day
        zoo = update_pets(zoo, total_minutes, today_str)
    else:
        zoo = update_pets(zoo, total_minutes, today_str)

# ---------- Run ----------
if __name__ == "__main__":
    analyze_today()
