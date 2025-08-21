# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt
from streamlit_extras.metric_cards import style_metric_cards
from datetime import datetime
from pet_manager import load_zoo
import os

# ---------- Config ----------
ZOO_FILE = "pets.csv"
DAILY_HISTORY = "daily_history.csv"  # ✅ changed from DAILY_SUMMARY
ACCUMULATION_FILE = "accumulated_minutes.csv"
EVOLUTION_THRESHOLD = 14 * 60  # 14 hours
MAX_LEVEL = 3
ASSETS_PATH = "assets"  # where pet gifs live: assets/<pet>_level<level>.gif

# ---------- Helpers ----------
def get_pet_image(pet_type: str, level: int) -> str:
    filename = f"{str(pet_type).lower()}_level{int(level)}.gif"
    return os.path.join(ASSETS_PATH, filename)

def load_summary() -> pd.DataFrame:
    return pd.read_csv(DAILY_HISTORY) if os.path.exists(DAILY_HISTORY) else pd.DataFrame()  # ✅

def load_accumulation() -> pd.DataFrame:
    return pd.read_csv(ACCUMULATION_FILE) if os.path.exists(ACCUMULATION_FILE) else pd.DataFrame()

def pet_progress_gauge(cumulative_minutes: float, pet_type: str, level: int):
    mins_left = max(0.0, EVOLUTION_THRESHOLD - float(cumulative_minutes))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(cumulative_minutes),
        number={'suffix': " mins"},
        title={'text': f"{str(pet_type).capitalize()} — Level {int(level)}"},
        gauge={
            'axis': {'range': [0, EVOLUTION_THRESHOLD]},
            'bar': {'color': "green"},
            'steps': [{'range': [0, EVOLUTION_THRESHOLD], 'color': "lightgray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': EVOLUTION_THRESHOLD
            }
        }
    ))
    return fig, mins_left

def productivity_rating(summary: pd.DataFrame) -> str:
    if summary.empty or "Minutes" not in summary.columns or "Category" not in summary.columns:
        return "No Data"
    total = float(summary["Minutes"].sum())
    if total <= 0:
        return "No Data"
    good = float(summary.loc[summary["Category"] == "Good", "Minutes"].sum())
    neutral = float(summary.loc[summary["Category"] == "Neutral", "Minutes"].sum())
    score = (good + 0.5 * neutral) / total
    if score >= 0.75:
        return "🌟 Excellent"
    elif score >= 0.6:
        return "💪 Good"
    elif score >= 0.4:
        return "🙂 Average"
    else:
        return "⚠️ Poor"

# ---------- Streamlit ----------
st.set_page_config(page_title="🐾 Pet Productivity Dashboard", layout="wide")
st.title("🐾 Productivity Pet Dashboard")

st.markdown("""
    <style>
    [data-testid="column"] {
        flex: 1 !important;
        min-width: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.header("📅 Select Date")
acc = load_accumulation()
if not acc.empty and "date" in acc.columns:
    acc["date"] = pd.to_datetime(acc["date"], errors="coerce")
    acc = acc.dropna(subset=["date"])
    available_dates = sorted(acc["date"].dt.date.unique())
    if available_dates:
        selected_date = st.sidebar.date_input(
            "Choose a day:",
            available_dates[-1],
            min_value=min(available_dates),
            max_value=max(available_dates),
        )
    else:
        selected_date = datetime.today().date()
else:
    selected_date = datetime.today().date()

# ---------- Pets ----------
st.header("🐾 Your Pet Productivity Zoo")
zoo = load_zoo()
if zoo.empty:
    st.info("No pets yet. Stay productive to unlock your first companion! 🎉")
else:
    zoo["cumulative_minutes"] = pd.to_numeric(zoo.get("cumulative_minutes", 0.0), errors="coerce").fillna(0.0)
    zoo["level"] = pd.to_numeric(zoo.get("level", 1), errors="coerce").fillna(1).astype(int)
    total_time_hours = zoo["cumulative_minutes"].sum() / 60.0
    st.markdown(f"**Total Time Logged:** {total_time_hours:.2f} hrs | **Total Pets Collected:** {len(zoo)}")

    st.subheader("🦄 Pet Collection")

    for i, pet in zoo.iterrows():
        pet_type_raw = str(pet.get("pet_type", ""))
        pet_type = pet_type_raw.capitalize()
        level = int(pet.get("level", 1))
        cumulative_minutes = float(pet.get("cumulative_minutes", 0.0))
        adopted = pet.get("start_date", "—")
        last_active = pet.get("last_updated", "—")

        col_info, col_img, col_gauge = st.columns([1.5, 1, 1.2], gap="large")

        with col_info:
            st.markdown(f"### 🐾 {pet_type} (Lvl {level})")
            st.write(f"🗓️ **Adopted:** {adopted}")
            st.write(f"🕒 **Last Active:** {last_active}")
            st.write(f"⏱️ **Total Time:** {cumulative_minutes/60:.2f} hrs")

        with col_img:
            img_path = get_pet_image(pet_type_raw, level)
            if os.path.exists(img_path):
                st.image(img_path, width=180)
            else:
                st.warning(f"🐾 Missing image for {pet_type} level {level}")

        with col_gauge:
            if level < MAX_LEVEL:
                fig, mins_left = pet_progress_gauge(cumulative_minutes, pet_type_raw, level)
                fig.update_layout(height=240, margin=dict(l=6, r=6, t=36, b=6))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"⏳ {mins_left:.1f} mins until next evolution")
            else:
                st.success("🌟 Max evolution reached!")

# ---------- Productivity Summary ----------
st.header(f"📊 Productivity on {selected_date}")
summary = load_summary()

if not summary.empty:
    if "date" in summary.columns:
        summary["date"] = pd.to_datetime(summary["date"], errors="coerce").dt.date
        summary = summary[summary["date"] == selected_date]

    summary = summary.rename(columns={
        "app": "Application",
        "minutes": "Minutes",
        "productivity": "Category"
    })

    summary["Minutes"] = pd.to_numeric(summary.get("Minutes", 0), errors="coerce").fillna(0.0)
    rating = productivity_rating(summary)

    st.subheader(f"⭐ Productivity Rating: {rating}")

    chart = alt.Chart(summary).mark_bar().encode(
        x=alt.X('Application:N', sort='-y', title='Application'),
        y=alt.Y('Minutes:Q', title='Minutes'),
        color=alt.Color('Category:N', title='Category'),
        tooltip=['Application', 'Minutes', 'Category']
    ).properties(height=320)
    st.altair_chart(chart, use_container_width=True)

    st.dataframe(
        summary.style.background_gradient(cmap="Greens", subset=["Minutes"]),
        use_container_width=True
    )

    st.subheader("🏆 Top 5 Apps")
    top5 = summary.sort_values("Minutes", ascending=False).head(5).copy()
    st.bar_chart(top5.set_index("Application")["Minutes"])
    st.dataframe(top5, use_container_width=True)

    st.subheader("🚫 Least Used Distractions")
    distractions = summary[summary["Category"] == "Bad"].sort_values("Minutes", ascending=True).head(5)
    if distractions.empty:
        st.write("No distractions logged today 🎉")
    else:
        st.table(distractions[["Application", "Minutes"]])
else:
    st.write("No productivity data for this day yet.")

# ---------- Historical Trend ----------
st.header("📈 Time Tracked Over Days")
if not acc.empty and "date" in acc.columns:
    acc_plot = acc.copy()
    acc_plot["date"] = pd.to_datetime(acc_plot["date"], errors="coerce")
    acc_plot = acc_plot.dropna(subset=["date"])
    st.line_chart(acc_plot.set_index("date")["minutes"])
else:
    st.write("No historical data yet.")

# ---------- Streaks & Milestones ----------
st.header("🏆 Milestones & Streaks")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🔥 Current Streak", "—")  # Optional: pull from activity file if needed
with col2:
    st.metric("⭐ Milestone", "14h per level")
with col3:
    total_mins = float(acc["minutes"].sum()) if ("minutes" in acc.columns and not acc.empty) else 0.0
    st.metric("🎯 Total Productivity", f"{total_mins:.1f} mins")

style_metric_cards(background_color="#f0f9f9", border_left_color="#00aaff")

st.caption("Keep focusing — more pets will unlock at streak milestones! 🐼🐶🐱🐢🐉🦊")
