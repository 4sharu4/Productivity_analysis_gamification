# app.py
import streamlit as st
import pandas as pd
from pathlib import Path

# Paths
ZOO_FILE = "pets.csv"
SUMMARY_FILE = "daily_summary.csv"
ASSETS_FOLDER = "assets"

st.set_page_config(page_title="Pet Tracker", page_icon="🐾")

st.title("🐾 Your Productivity Zoo")

# --- Show today's activity ---
st.header("📊 Today's App Usage")

if Path(SUMMARY_FILE).exists():
    df = pd.read_csv(SUMMARY_FILE)
    st.dataframe(df[["app", "minutes"]])
else:
    st.info("No usage data yet. Run tracker.py and analyze.py today.")

# --- Show your pets ---
st.header("🦴 Your Pets")

if Path(ZOO_FILE).exists():
    zoo = pd.read_csv(ZOO_FILE)
    for _, pet in zoo.iterrows():
        pet_type = str(pet["pet_type"])
        level = int(pet["level"])
        gif_path = f"{ASSETS_FOLDER}/{pet_type}_level{level}.gif"

        cols = st.columns([1, 2])
        with cols[0]:
            if Path(gif_path).exists():
                st.image(gif_path, width=120)
            else:
                st.warning(f"Missing image: {gif_path}")
        with cols[1]:
            st.subheader(f"{pet_type.title()} (Level {level})")
            st.text(f"Started: {pet['start_date']}")
            st.text(f"Last Active: {pet['last_updated']}")
else:
    st.info("No pets yet! Run analyze.py after some activity to unlock your first pet.")
