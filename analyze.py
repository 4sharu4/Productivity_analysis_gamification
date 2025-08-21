from datetime import datetime, timedelta
import pandas as pd
import random
import os

# Constants
LOG_FILE = "usage_log.csv"
ZOO_FILE = "pets.csv"
DAILY_SUMMARY = "daily_summary.csv"
ACTIVITY_FILE = "activity_dates.csv"

SAMPLE_SECONDS = 15  # Should match tracker.py
ACCUMULATION_FILE = "accumulated_minutes.csv"

# Thresholds
EVOLUTION_THRESHOLD = 14 * 60  # 14 hours in minutes
MAX_LEVEL = 3

# Streak-based pet unlocks
NEW_PET_STREAKS = {1, 2, 5, 10, 15, 20, 30, 50, 100}

# Productivity mapping
PRODUCTIVITY = {
    "vs code": "Good",
    "email": "Good",
    "docs": "Good",
    "notepad": "Neutral",
    "youtube": "Bad",
    "netflix": "Bad",
    "games": "Bad",
    "other": "Neutral"
}

# Pet pool (use game-style names that match your assets)
PET_TYPES = ["cat", "dog", "fox", "dragon", "panda", "turtle"]

# ----------- Helper Functions -----------

def clean_app_name(name):
    name = str(name).lower()
    if "youtube" in name:
        return "YouTube"
    elif "chrome" in name:
        return "Chrome"
    elif "vs code" in name or "visual studio" in name:
        return "VS Code"
    elif "mail" in name:
        return "Email"
    elif "netflix" in name:
        return "Netflix"
    elif "notepad" in name:
        return "Notepad"
    elif "game" in name:
        return "Games"
    else:
        return "Other"

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

def mark_activity_today():
    today = datetime.now().date().strftime("%Y-%m-%d")
    if os.path.exists(ACTIVITY_FILE):
        df = pd.read_csv(ACTIVITY_FILE)
    else:
        df = pd.DataFrame(columns=["date"])
    if today not in df["date"].astype(str).values:
        df.loc[len(df)] = [today]
        df.to_csv(ACTIVITY_FILE, index=False)

# ----------- Main Analysis -----------

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

    # Time calculations
    total_samples = len(df_today)
    total_minutes = total_samples * SAMPLE_SECONDS / 60.0

    summary = df_today["app"].value_counts().rename_axis("app").reset_index(name="samples")
    summary["minutes"] = summary["samples"] * SAMPLE_SECONDS / 60.0
    summary["productivity"] = summary["app"].apply(lambda x: PRODUCTIVITY.get(x.lower(), "Neutral"))
    summary.sort_values("minutes", ascending=False).to_csv(DAILY_SUMMARY, index=False)

    # Save total accumulation (rolling across days)
    if os.path.exists(ACCUMULATION_FILE):
        acc_df = pd.read_csv(ACCUMULATION_FILE)
    else:
        acc_df = pd.DataFrame(columns=["date", "minutes"])

    acc_df.loc[len(acc_df)] = [str(today), total_minutes]
    acc_df.to_csv(ACCUMULATION_FILE, index=False)

    mark_activity_today()
    streak = compute_streak()
    print(f"Tracked {total_minutes:.1f} minutes today — streak: {streak} day(s)")

    # Load or init zoo
    if os.path.exists(ZOO_FILE):
        zoo = pd.read_csv(ZOO_FILE)
    else:
        zoo = pd.DataFrame(columns=["date", "pet", "level"])

    # Unlock pet if:
    # - First day
    # - OR streak matches milestone
    pet_unlocked = False
    if zoo.empty or streak in NEW_PET_STREAKS:
        new_pet = random.choice(PET_TYPES)
        zoo.loc[len(zoo)] = [str(today), new_pet, 1]
        print(f"🎉 New pet unlocked: {new_pet} (Level 1)")
        pet_unlocked = True
    else:
        # Level up logic
        num_pets = len(zoo)
        split_minutes = total_minutes / num_pets

        for i in zoo.index:
            current_level = zoo.at[i, "level"]
            if current_level < MAX_LEVEL:
                if split_minutes >= EVOLUTION_THRESHOLD:
                    zoo.at[i, "level"] += 1
                    print(f"⬆️ {zoo.at[i, 'pet']} leveled up to {zoo.at[i, 'level']}")
                    break
        else:
            # No pet leveled up AND all at max level → unlock new pet
            if all(zoo["level"] >= MAX_LEVEL):
                new_pet = random.choice(PET_TYPES)
                zoo.loc[len(zoo)] = [str(today), new_pet, 1]
                print(f"✨ New generation begins: {new_pet} (Level 1)")

    # Save zoo
    zoo.to_csv(ZOO_FILE, index=False)

# ----------- Run Script -----------

if __name__ == "__main__":
    analyze_today()