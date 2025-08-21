# pet_manager.py
from pathlib import Path
import pandas as pd
import random
from datetime import datetime

ZOO_FILE = "pets.csv"
PET_TYPES = ["cat", "dog", "panda", "fox", "turtle", "dragon"]  # match assets/<pet>_level*.gif

def load_zoo():
    """Return pets DataFrame, or empty structured DF if file missing."""
    if Path(ZOO_FILE).exists():
        df = pd.read_csv(ZOO_FILE)
        # ensure columns exist
        expected = ["pet_id", "pet_type", "level", "start_date", "last_updated"]
        for c in expected:
            if c not in df.columns:
                df[c] = None
        return df
    else:
        return pd.DataFrame(columns=["pet_id", "pet_type", "level", "start_date", "last_updated"])

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
    """
    Add a new pet row to df, save, and return (df, pet_type, level).
    """
    pet_type = choose_new_pet(list(df["pet_type"].astype(str).unique()))
    pet_id = _next_pet_id(df)
    today = datetime.now().strftime("%Y-%m-%d")
    new_row = {
        "pet_id": pet_id,
        "pet_type": pet_type,
        "level": 1,
        "start_date": today,
        "last_updated": today,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_zoo(df)
    return df, pet_type, 1

def level_up_last_pet(df):
    """
    Increment level of the most recent pet (by DataFrame order).
    If no pet exists, create first pet.
    Returns (df, pet_type, new_level).
    """
    if df.empty:
        return record_new_pet(df)
    last_idx = df.index.max()
    try:
        df.loc[last_idx, "level"] = int(df.loc[last_idx, "level"]) + 1
    except Exception:
        df.loc[last_idx, "level"] = 2
    df.loc[last_idx, "last_updated"] = datetime.now().strftime("%Y-%m-%d")
    pet_type = df.loc[last_idx, "pet_type"]
    new_level = int(df.loc[last_idx, "level"])
    save_zoo(df)
    return df, pet_type, new_level
