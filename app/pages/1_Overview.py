# app/pages/1_Overview.py

import streamlit as st
import pandas as pd
from sqlalchemy import text
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

from src.db_utils import get_engine

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

# ---------- Helpers & data loaders ----------

@st.cache_data(show_spinner=False)
def load_daily():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM weather_daily ORDER BY date;", engine, parse_dates=["date"])
    return df

@st.cache_data(show_spinner=False)
def load_hourly_for_day(d: date):
    """Lấy dữ liệu theo giờ cho một ngày cụ thể từ weather_raw."""
    engine = get_engine()
    q = """
        SELECT timestamp, date,
               temp_out, out_hum,
               wind_speed, bar, solar_rad, rain
        FROM weather_raw
        WHERE date = :d
        ORDER BY timestamp;
    """
    params = {"d": d}
    df = pd.read_sql(text(q), engine, params=params, parse_dates=["timestamp", "date"])
    if not df.empty:
        # resample 1H
        df = (
            df.set_index("timestamp")
              .resample("1H")
              .mean()
              .reset_index()
        )
    return df

def classify_condition(total_rain, mean_solar, mean_wind):
    if pd.isna(total_rain):
        total_rain = 0
    if pd.isna(mean_solar):
        mean_solar = 0
    if pd.isna(mean_wind):
        mean_wind = 0

    if total_rain > 10:
        return "🌧️ Heavy Rain"
    if total_rain > 0.5:
        return "🌦️ Rain Showers"
    if mean_solar > 250 and total_rain == 0:
        return "☀️ Clear Sky"
    if mean_wind > 8:
        return "💨 Windy"
    return "⛅ Partly Cloudy"


def get_temp_color(temp, min_temp=-10, max_temp=35):
    """Trả về màu từ xanh (lạnh) đến đỏ (nóng) dựa trên nhiệt độ"""
    import numpy as np
    # Normalize temp về [0, 1]
    normalized = (temp - min_temp) / (max_temp - min_temp)
    normalized = max(0, min(1, normalized))  # Clamp to [0, 1]
    
    # Blue (cold) -> Cyan -> Yellow -> Red (hot)
    if normalized < 0.33:
        # Blue to Cyan
        r = int(0 + (0 * normalized * 3))
        g = int(100 + (155 * normalized * 3))
        b = int(255)
    elif normalized < 0.66:
        # Cyan to Yellow
        r = int(0 + (255 * (normalized - 0.33) * 3))
        g = 255
        b = int(255 - (255 * (normalized - 0.33) * 3))
    else:
        # Yellow to Red
        r = 255
        g = int(255 - (255 * (normalized - 0.66) * 3))
        b = 0
    
    return f"rgb({r}, {g}, {b})"


def get_rain_color(rain, max_rain=50):
    """Trả về màu từ xanh nhạt đến xanh đậm dựa trên lượng mưa"""
    import numpy as np
    normalized = min(rain / max_rain, 1.0)
    # Light blue to dark blue
    r = int(173 - (73 * normalized))
    g = int(216 - (16 * normalized))
    b = int(230 - (30 * normalized))
    return f"rgb({r}, {g}, {b})"


def get_wind_color(wind, max_wind=20):
    """Trả về màu từ vàng đến đỏ dựa trên tốc độ gió"""
    import numpy as np
    normalized = min(wind / max_wind, 1.0)
    # Yellow to Red
    r = int(255)
    g = int(255 - (255 * normalized))
    b = int(0)
    return f"rgb({r}, {g}, {b})"


def get_pressure_color(pressure, min_pressure=950, max_pressure=1050):
    """Trả về màu từ đỏ (thấp) đến xanh (cao) dựa trên áp suất"""
    import numpy as np
    normalized = (pressure - min_pressure) / (max_pressure - min_pressure)
    normalized = max(0, min(1, normalized))
    # Red (low) to Blue (high)
    r = int(255 - (255 * normalized))
    g = int(0)
    b = int(0 + (255 * normalized))
    return f"rgb({r}, {g}, {b})"


def get_humidity_color(humidity):
    """Trả về màu từ vàng (khô) đến xanh (ẩm) dựa trên độ ẩm"""
    import numpy as np
    normalized = humidity / 100.0
    # Yellow (dry) to Blue (humid)
    r = int(255 - (255 * normalized))
    g = int(255 - (155 * normalized))
    b = int(0 + (255 * normalized))
    return f"rgb({r}, {g}, {b})"


# ---------- Page ----------

st.title("📊 Overview")

df_daily = load_daily()
if df_daily.empty:
    st.warning("No daily data available.")
    st.stop()

min_date = df_daily["date"].min().date()
max_date = df_daily["date"].max().date()

with st.sidebar:
    st.header("Global Filters")

    # Focus date dùng cho Today card & gauge
    focus_date = st.date_input(
        "Focus date (for 'Today' view)",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )

    # Date range cho các chart tổng thể
    dr = st.date_input(
        "Date range (for charts)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(dr, tuple) and len(dr) == 2:
        date_from, date_to = dr
    else:
        date_from, date_to = min_date, max_date

city_name = "Bradford, UK"

# lọc daily cho range
mask = (df_daily["date"] >= pd.to_datetime(date_from)) & (df_daily["date"] <= pd.to_datetime(date_to))
df_range = df_daily[mask].copy()
if df_range.empty:
    st.warning("No data in selected range.")
    st.stop()

# row của focus date
row_focus = df_daily[df_daily["date"] == pd.to_datetime(focus_date)]
if row_focus.empty:
    st.warning("Focus date not found in daily table.")
    st.stop()
row_focus = row_focus.iloc[0]


# ---------- Hàng 1: Today card + gauges ----------

c1, c2, c3, c4 = st.columns([1.4, 1, 1, 1])

with c1:
    # Today card
    date_str_pretty = pd.to_datetime(focus_date).strftime("%a, %d %b %Y")
    mean_temp = row_focus["mean_temp"]
    cond_text = classify_condition(
        row_focus["total_rain"],
        row_focus["mean_solar"],
        row_focus["mean_wind_speed"],
    )

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,#4CAF50,#81C784);
            border-radius: 20px;
            padding: 20px 24px;
            color: white;
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        ">
          <div style="font-size: 22px; font-weight: 600;">{city_name}</div>
          <div style="font-size: 14px; opacity: 0.9; margin-top: 4px;">{date_str_pretty}</div>
          <div style="font-size: 42px; font-weight: 700; margin-top: 16px;">{mean_temp:.1f}°C</div>
          <div style="font-size: 20px; margin-top: 8px;">{cond_text}</div>
          <div style="margin-top: 16px; font-size: 14px;">
            High: {row_focus['max_temp']:.1f}°C &nbsp;&nbsp;•&nbsp;&nbsp;
            Low: {row_focus['min_temp']:.1f}°C &nbsp;&nbsp;•&nbsp;&nbsp;
            Rain: {row_focus['total_rain']:.1f} mm
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    # Temperature gauge (so sánh với toàn bộ range)
    temp_min_all = df_daily["min_temp"].min()
    temp_max_all = df_daily["max_temp"].max()

    fig_temp_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(mean_temp),
            title={"text": "Mean Temp (°C)"},
            gauge={
                "axis": {"range": [temp_min_all, temp_max_all]},
            },
        )
    )
    fig_temp_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_temp_gauge, use_container_width=True)

with c3:
    # Humidity gauge
    mean_hum = row_focus["mean_humidity"]

    fig_hum_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(mean_hum),
            title={"text": "Humidity (%)"},
            gauge={"axis": {"range": [0, 100]}},
        )
    )
    fig_hum_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_hum_gauge, use_container_width=True)

with c4:
    # Wind Speed gauge
    mean_wind = row_focus["mean_wind_speed"]
    max_wind = row_focus["max_wind_speed"]
    wind_max_all = df_daily["max_wind_speed"].max()

    fig_wind_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(mean_wind),
            title={"text": "Wind Speed (m/s)"},
            gauge={
                "axis": {"range": [0, max(20, wind_max_all * 1.2)]},
            },
        )
    )
    fig_wind_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_wind_gauge, use_container_width=True)
    
    # Hiển thị max wind speed bên dưới gauge
    st.markdown(
        f"""
        <div style="
            margin-top: 8px;
            text-align: center;
            font-size: 13px;
            color: rgba(255, 255, 255, 0.7);
        ">
          Max: {max_wind:.1f} m/s
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Hàng 2: Today hourly chart ----------

st.subheader("Today – Hourly Profile")

df_hourly = load_hourly_for_day(focus_date)
if df_hourly.empty:
    st.info("No hourly raw data available for this day.")
else:
    col_ts1, col_ts2 = st.columns(2)
    with col_ts1:
        fig_ht = px.line(
            df_hourly,
            x="timestamp",
            y="temp_out",
            title="Temperature by hour",
            labels={"timestamp": "Time", "temp_out": "Temp (°C)"},
        )
        st.plotly_chart(fig_ht, use_container_width=True)
    with col_ts2:
        fig_hr = px.bar(
            df_hourly,
            x="timestamp",
            y="rain",
            title="Rainfall by hour",
            labels={"timestamp": "Time", "rain": "Rain (mm)"},
        )
        st.plotly_chart(fig_hr, use_container_width=True)


# ---------- Hàng 3: Highlights for selected range ----------

st.subheader("Highlights over selected period")

c_h1, c_h2, c_h3, c_h4 = st.columns(4)

# Tính toán các giá trị
avg_temp = df_range['mean_temp'].mean()
min_temp = df_range['min_temp'].min()
max_temp = df_range['max_temp'].max()
total_rain = df_range['total_rain'].sum()
rainy_days = int((df_range['total_rain'] > 0.5).sum())
avg_wind = df_range['mean_wind_speed'].mean()
max_wind = df_range['max_wind_speed'].max()
avg_pressure = df_range['mean_pressure'].mean()
avg_humidity = df_range['mean_humidity'].mean()

# Tính toán màu sắc
temp_color = get_temp_color(avg_temp)
min_temp_color = get_temp_color(min_temp)
max_temp_color = get_temp_color(max_temp)
rain_color = get_rain_color(total_rain)
wind_color = get_wind_color(avg_wind)
max_wind_color = get_wind_color(max_wind)
pressure_color = get_pressure_color(avg_pressure)
humidity_color = get_humidity_color(avg_humidity)

with c_h1:
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Average Temp (°C)</div>
            <div style="font-size: 32px; font-weight: 600; color: {temp_color};">{avg_temp:.1f}</div>
        </div>
        <div>
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Temp range (min / max)</div>
            <div style="font-size: 20px; font-weight: 600;">
                <span style="color: {min_temp_color};">{min_temp:.1f}°</span> / 
                <span style="color: {max_temp_color};">{max_temp:.1f}°</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_h2:
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Total Rain (mm)</div>
            <div style="font-size: 32px; font-weight: 600; color: {rain_color};">{total_rain:.1f}</div>
        </div>
        <div>
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Rainy days</div>
            <div style="font-size: 32px; font-weight: 600; color: {rain_color};">{rainy_days}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_h3:
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Avg Wind Speed (m/s)</div>
            <div style="font-size: 32px; font-weight: 600; color: {wind_color};">{avg_wind:.1f}</div>
        </div>
        <div>
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Max Wind Speed (m/s)</div>
            <div style="font-size: 32px; font-weight: 600; color: {max_wind_color};">{max_wind:.1f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_h4:
    st.markdown(
        f"""
        <div style="margin-bottom: 20px;">
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Avg Pressure (mb)</div>
            <div style="font-size: 32px; font-weight: 600; color: {pressure_color};">{avg_pressure:.0f}</div>
        </div>
        <div>
            <div style="font-size: 14px; color: rgba(255,255,255,0.7); margin-bottom: 4px;">Avg Humidity (%)</div>
            <div style="font-size: 32px; font-weight: 600; color: {humidity_color};">{avg_humidity:.0f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Bonus: calendar-like heatmap for the whole range ----------

st.subheader("Calendar-style temperature heatmap")

df_cal = df_range.copy()
df_cal["day"] = df_cal["date"].dt.day
df_cal["month_name"] = df_cal["date"].dt.month_name().str.slice(stop=3)

fig_cal = px.density_heatmap(
    df_cal,
    x="day",
    y="month_name",
    z="mean_temp",
    color_continuous_scale="Turbo",
    labels={"day": "Day", "month_name": "Month", "mean_temp": "Mean Temp (°C)"},
    title="Daily mean temperature",
)
st.plotly_chart(fig_cal, use_container_width=True)
