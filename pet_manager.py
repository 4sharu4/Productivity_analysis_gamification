from pathlib import Path
import pandas as pd
import random
from datetime import datetime

ZOO_FILE = "pets.csv"
PET_TYPES = ["cat", "dog", "panda", "fox", "turtle", "dragon"]  # match assets/<pet>_level*.gif
MAX_LEVEL = 3
EVOLUTION_THRESHOLD = 14 * 60  # 14 hours = 840 min

def load_zoo():
    """Return pets DataFrame, or empty structured DF if file missing."""
    if Path(ZOO_FILE).exists():
        df = pd.read_csv(ZOO_FILE)
    else:
        df = pd.DataFrame(columns=[
            "pet_id", "pet_type", "level",
            "start_date", "last_updated", "cumulative_minutes"
        ])

    # Ensure required columns exist with defaults
    if "pet_id" not in df.columns:
        df["pet_id"] = []
    if "pet_type" not in df.columns:
        df["pet_type"] = []
    if "level" not in df.columns:
        df["level"] = []
    if "start_date" not in df.columns:
        df["start_date"] = []
    if "last_updated" not in df.columns:
        df["last_updated"] = []
    if "cumulative_minutes" not in df.columns:
        df["cumulative_minutes"] = []

    # Default values
    df["level"] = df["level"].fillna(1).astype(int)
    df["cumulative_minutes"] = df["cumulative_minutes"].fillna(0.0).astype(float)
    return df

def save_zoo(df):
    """Save the zoo DataFrame to CSV."""
    df.to_csv(ZOO_FILE, index=False)

def _next_pet_id(df):
    """Compute next pet id (int)."""
    if df.empty:
        return 1
    try:
        return int(df["pet_id"].max()) + 1
    except Exception:
        return len(df) + 1

def choose_new_pet(existing_types):
    """Prefer an unused pet type if available, else random from all."""
    unused = [p for p in PET_TYPES if p not in existing_types]
    pool = unused if unused else PET_TYPES
    return random.choice(pool)

def record_new_pet(df):
    """Add a new pet row to df, save, and return (df, pet_type, level)."""
    pet_type = choose_new_pet(list(df["pet_type"].astype(str).unique()))
    pet_id = _next_pet_id(df)
    today = datetime.now().strftime("%Y-%m-%d")
    new_row = {
        "pet_id": pet_id,
        "pet_type": pet_type,
        "level": 1,
        "start_date": today,
        "last_updated": today,
        "cumulative_minutes": 0.0,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_zoo(df)
    return df, pet_type, 1

def update_pets(df, total_minutes, today_str):
    """Distribute today's minutes across pets, evolve them if thresholds met."""
    if df.empty:
        print("No pets to update.")
        return df

    num_pets = len(df)
    split_minutes = total_minutes / num_pets
    print(f"Distributing {total_minutes} total minutes across {num_pets} pets ({split_minutes} each)")

    for i in df.index:
        print(f"Before: Pet {df.at[i, 'pet_type']} has {df.at[i, 'cumulative_minutes']:.2f} mins")
        df.at[i, "cumulative_minutes"] += split_minutes
        print(f"After: Pet {df.at[i, 'pet_type']} has {df.at[i, 'cumulative_minutes']:.2f} mins")

        while df.at[i, "level"] < MAX_LEVEL and df.at[i, "cumulative_minutes"] >= EVOLUTION_THRESHOLD:
            df.at[i, "level"] += 1
            df.at[i, "cumulative_minutes"] -= EVOLUTION_THRESHOLD
            df.at[i, "last_updated"] = today_str
            print(f"⬆️ {df.at[i, 'pet_type']} leveled up to {df.at[i, 'level']}")

    save_zoo(df)
    return df
