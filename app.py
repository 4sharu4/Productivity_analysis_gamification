import streamlit as st
import pandas as pd
import datetime
import os
from PIL import Image
import matplotlib.pyplot as plt

# Files
LOG_FILE = "usage_log.csv"
ZOO_FILE = "pets.csv"

# Productivity ratings (you can adjust)
PRODUCTIVITY = {
    "YouTube": "Bad",
    "Chrome": "Neutral",
    "VS Code": "Good",
    "Email": "Neutral",
    "Other": "Neutral",
}

def load_data():
    # Load logs and pets
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
    else:
        df = pd.DataFrame(columns=["timestamp", "app"])

    if os.path.exists(ZOO_FILE):
        zoo = pd.read_csv(ZOO_FILE)
    else:
        zoo = pd.DataFrame(columns=["date", "pet", "level"])
    return df, zoo

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
    else:
        return "Other"

def main():
    st.title("🐾 Pet Tracker Dashboard")

    df, zoo = load_data()
    if df.empty:
        st.warning("No usage data found. Run tracker.py to log app usage.")
        return

    # Clean app names
    df["app"] = df["app"].apply(clean_app_name)

    # Date filter
    min_date = df["timestamp"].dt.date.min()
    max_date = df["timestamp"].dt.date.max()
    date_range = st.sidebar.date_input(
        "Select date range", [min_date, max_date],
        min_value=min_date, max_value=max_date
    )
    if len(date_range) != 2:
        st.error("Please select a start and end date")
        return
    start_date, end_date = date_range

    df_filtered = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]

    if df_filtered.empty:
        st.warning("No data for the selected date range.")
        return

    # Total time spent in minutes
    total_samples = len(df_filtered)
    SAMPLE_SECONDS = 15  # Must match tracker and analyze.py
    total_minutes = total_samples * SAMPLE_SECONDS / 60.0
    total_hours = total_minutes / 60.0

    # Pets summary
    pet_count = len(zoo)
    pet_names = zoo["pet"].tolist()
    pet_levels = zoo["level"].tolist()

    # Show summary cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Hours Tracked", f"{total_hours:.2f} hrs")
        st.metric("Pet Count", pet_count)

    with col2:
        if pet_count > 0:
            st.markdown("### Latest Pet")
            latest_pet = zoo.iloc[-1]
            st.write(f"**Name:** {latest_pet['pet'].capitalize()}")
            st.write(f"**Level:** {latest_pet['level']}")

            # Show pet image if exists
            img_path = f"pets/{latest_pet['pet']}_level{latest_pet['level']}.png"
            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, width=150)
            else:
                st.info("Pet image not found.")
        else:
            st.write("No pets unlocked yet.")

    with col3:
        # Plot distribution of app usage
        usage_counts = df_filtered["app"].value_counts()
        st.markdown("### App Usage Distribution")
        fig, ax = plt.subplots()
        usage_counts.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_ylabel("Samples (15s each)")
        ax.set_xlabel("App")
        st.pyplot(fig)

    # Most frequently visited app
    most_used_app = df_filtered["app"].mode()[0]
    st.markdown(f"### Most Frequently Used App: **{most_used_app}**")

    # Per-app productivity ratings table
    st.markdown("### Per-App Productivity Ratings")
    prod_df = pd.DataFrame({
        "App": list(PRODUCTIVITY.keys()),
        "Productivity": list(PRODUCTIVITY.values())
    })
    st.table(prod_df)

    # Top 5 apps used by time (descending)
    top5_apps = usage_counts.head(5)
    st.markdown("### Top 5 Apps by Usage")
    st.bar_chart(top5_apps)

    # Least productive apps - those rated 'Bad' and used for >0 time, sorted ascending by time
    bad_apps = [app for app, prod in PRODUCTIVITY.items() if prod == "Bad"]
    bad_app_usage = usage_counts.loc[usage_counts.index.isin(bad_apps)]
    bad_app_usage = bad_app_usage.sort_values()
    if not bad_app_usage.empty:
        st.markdown("### Least Productive Apps Usage")
        st.bar_chart(bad_app_usage)

    # Detailed session times table (group by app & day)
    st.markdown("### Detailed Session Times")
    df_filtered["date"] = df_filtered["timestamp"].dt.date
    session_summary = df_filtered.groupby(["date", "app"]).size().reset_index(name="samples")
    session_summary["minutes"] = session_summary["samples"] * SAMPLE_SECONDS / 60.0
    st.dataframe(session_summary.sort_values(["date", "minutes"], ascending=[False, False]))

if __name__ == "__main__":
    main()
