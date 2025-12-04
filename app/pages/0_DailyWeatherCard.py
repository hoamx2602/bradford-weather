# app/pages/0_DailyWeatherCard.py

import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import timedelta

from src.db_utils import get_engine

st.set_page_config(
    page_title="Daily Weather Card",
    page_icon="🌤️",
    layout="wide",
)

# ---------- CSS ----------
CARD_CSS = """
<style>
.weather-card {
    background: #4CAF50;
    border-radius: 20px;
    padding: 24px 32px;
    color: white;
    font-family: "Helvetica", "Arial", sans-serif;
    box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

.weather-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.weather-city {
    font-size: 24px;
    font-weight: 600;
}

.weather-date {
    font-size: 16px;
    margin-top: 4px;
    opacity: 0.9;
}

.weather-main-temp {
    font-size: 40px;
    font-weight: 700;
    margin-top: 8px;
}

.weather-main-status {
    font-size: 22px;
    font-weight: 500;
    margin-top: 12px;
}

.weather-icon {
    font-size: 56px;
    margin-bottom: 8px;
}

.weather-right {
    text-align: right;
    font-size: 16px;
}

.forecast-row {
    display: flex;
    justify-content: space-between;
    margin-top: 24px;
}

.forecast-card {
    flex: 1;
    text-align: center;
    padding: 8px 4px;
    margin: 0 4px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.12);
}

.forecast-day {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
}

.forecast-icon {
    font-size: 28px;
    margin-bottom: 4px;
}

.forecast-temp {
    font-size: 14px;
}
</style>
"""
st.markdown(CARD_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_daily():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM weather_daily ORDER BY date;", engine, parse_dates=["date"])
    return df


def classify_condition(row) -> tuple[str, str]:
    rain = row.get("total_rain", 0) or 0
    solar = row.get("mean_solar", 0) or 0
    wind = row.get("mean_wind_speed", 0) or 0

    if rain > 10:
        return "🌧️", "Heavy Rain"
    if rain > 0.5:
        return "🌦️", "Rain Showers"
    if solar > 250 and rain == 0:
        return "☀️", "Clear Sky"
    if wind > 8:
        return "💨", "Windy"
    return "⛅", "Partly Cloudy"


def weekday_short(date: pd.Timestamp) -> str:
    return date.strftime("%a").upper()  # MON, TUE, ...


st.title("🌤️ Daily Weather Card")

df_daily = load_daily()
if df_daily.empty:
    st.warning("No daily data available.")
    st.stop()

min_date = df_daily["date"].min().date()
max_date = df_daily["date"].max().date()

with st.sidebar:
    st.header("Select day")
    selected_date = st.date_input(
        "Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )

city_name = "Bradford, UK"

# Lấy row của ngày được chọn
row = df_daily[df_daily["date"] == pd.to_datetime(selected_date)]
if row.empty:
    st.error("Selected date not found in dataset.")
    st.stop()
row = row.iloc[0]

date_str_pretty = pd.to_datetime(selected_date).strftime("%a, %d %b %Y")

icon, status_text = classify_condition(row)

current_temp = row["mean_temp"]
wind = row["mean_wind_speed"]
precip_rate = row["total_rain"]
pressure = row["mean_pressure"]

# ---------- Forecast row HTML ----------
start = pd.to_datetime(selected_date)
end = start + timedelta(days=6)

df_forecast = df_daily[(df_daily["date"] >= start) & (df_daily["date"] <= end)].copy()
df_forecast = df_forecast.sort_values("date")

forecast_html_parts = ['<div class="forecast-row">']
for _, r in df_forecast.iterrows():
    f_icon, _ = classify_condition(r)
    day_label = weekday_short(r["date"])
    max_t = r["max_temp"]
    min_t = r["min_temp"]
    forecast_html_parts.append(
        f'<div class="forecast-card"><div class="forecast-day">{day_label}</div><div class="forecast-icon">{f_icon}</div><div class="forecast-temp">{max_t:.0f}°C / {min_t:.0f}°C</div></div>'
    )
forecast_html_parts.append("</div>")
forecast_html = "".join(forecast_html_parts)

# ---------- Card HTML ----------
card_html = f'<div class="weather-card"><div class="weather-header"><div><div class="weather-city">{city_name}</div><div class="weather-date">{date_str_pretty}</div><div class="weather-main-temp">{current_temp:.1f}°C</div><div class="weather-main-status">{status_text}</div></div><div class="weather-right"><div class="weather-icon">{icon}</div><div>Wind: {wind:.1f} m/s</div><div>Precip: {precip_rate:.1f} mm/day</div><div>Pressure: {pressure:.0f} mb</div></div></div>{forecast_html}</div>'

st.markdown(card_html, unsafe_allow_html=True)
