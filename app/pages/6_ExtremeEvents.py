# app/pages/6_ExtremeEvents.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from src.db_utils import get_engine

st.set_page_config(
    page_title="Extreme Events",
    page_icon="⚠️",
    layout="wide",
)

@st.cache_data(show_spinner=False)
def load_daily():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM weather_daily ORDER BY date;", engine, parse_dates=["date"])
    return df

@st.cache_data(show_spinner=False)
def load_raw_for_window(date_center, days_before=2, days_after=2):
    engine = get_engine()
    start = date_center - pd.Timedelta(days=days_before)
    end = date_center + pd.Timedelta(days=days_after)
    q = """
        SELECT timestamp, date,
               temp_out, out_hum,
               wind_speed, bar, solar_rad, rain_rate
        FROM weather_raw
        WHERE date BETWEEN :start AND :end
        ORDER BY timestamp;
    """
    params = {"start": start.date(), "end": end.date()}
    df = pd.read_sql(text(q), engine, params=params, parse_dates=["timestamp", "date"])
    return df

st.title("⚠️ Extreme Events")

df_daily = load_daily()
if df_daily.empty:
    st.warning("No daily data available.")
    st.stop()

df_daily["date_str"] = df_daily["date"].dt.strftime("%Y-%m-%d")

# xác định extreme type
df_daily["heavy_rain"] = df_daily["rain_flag"]
df_daily["strong_wind"] = df_daily["wind_flag"]
# simple heatwave/coldspell definition (top/bottom 5%)
temp_hi_thr = df_daily["max_temp"].quantile(0.95)
temp_lo_thr = df_daily["min_temp"].quantile(0.05)
df_daily["heatwave"] = df_daily["max_temp"] >= temp_hi_thr
df_daily["cold_spell"] = df_daily["min_temp"] <= temp_lo_thr

with st.sidebar:
    st.header("Event type")
    event_type = st.selectbox(
        "Choose extreme type",
        ["heavy_rain", "strong_wind", "heatwave", "cold_spell"],
        format_func=lambda x: {
            "heavy_rain": "Heavy rain",
            "strong_wind": "Strong wind",
            "heatwave": "Heatwave",
            "cold_spell": "Cold spell",
        }[x],
    )

    candidates = df_daily[df_daily[event_type]].copy()
    if candidates.empty:
        st.error(f"No events detected for {event_type}.")
        st.stop()

    event_date_str = st.selectbox(
        "Select an extreme day",
        candidates["date_str"].tolist(),
    )
    days_before = st.slider("Days before", 1, 5, 2)
    days_after = st.slider("Days after", 1, 5, 2)

event_date = pd.to_datetime(event_date_str)

st.subheader(f"Selected event: {event_type} on {event_date.date()}")

# --- Daily comparison: extreme vs non-extreme ---
st.markdown("### Distribution comparison (extreme vs non-extreme days)")

ext_mask = df_daily[event_type]
df_ext = df_daily[ext_mask]
df_non = df_daily[~ext_mask]

long = pd.concat([
    df_ext.assign(group="extreme"),
    df_non.assign(group="non_extreme"),
])

metrics = ["mean_temp", "total_rain", "mean_wind_speed", "mean_pressure"]

fig_box = px.box(
    long,
    x="group",
    y=st.selectbox("Variable to compare", metrics, index=0),
    points="all",
    title="Extreme vs non-extreme distribution",
)
st.plotly_chart(fig_box, use_container_width=True)

# --- Time window around event ---
st.markdown("### Time window around the event")

df_window = load_raw_for_window(event_date, days_before=days_before, days_after=days_after)

if df_window.empty:
    st.warning("No raw data for selected window.")
else:
    ts_vars = ["temp_out", "out_hum", "wind_speed", "bar"]
    tabs = st.tabs(ts_vars)
    for var, tab in zip(ts_vars, tabs):
        with tab:
            fig_ts = px.line(
                df_window,
                x="timestamp",
                y=var,
                title=f"{var} around event",
                labels={"timestamp": "Time", var: var},
            )
            # highlight event day
            # Use add_shape instead of add_vline to avoid Timestamp arithmetic issues
            event_datetime = pd.to_datetime(event_date)
            y_min = df_window[var].min()
            y_max = df_window[var].max()
            fig_ts.add_shape(
                type="line",
                x0=event_datetime,
                x1=event_datetime,
                y0=y_min,
                y1=y_max,
                yref="y",
                line=dict(dash="dash", color="red", width=2),
            )
            # Add annotation for event day
            fig_ts.add_annotation(
                x=event_datetime,
                y=y_max,
                yref="y",
                text="Event day",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                bgcolor="white",
                bordercolor="red",
            )
            st.plotly_chart(fig_ts, use_container_width=True)

# --- Simple daily timeline marking all events of this type ---
st.markdown("### All detected events of this type")

fig_timeline = px.scatter(
    df_daily,
    x="date",
    y="mean_temp",
    color=df_daily[event_type].map({True: "event", False: "other"}),
    size="total_rain",
    title="Timeline with highlighted extreme days",
    labels={"mean_temp": "Mean temp (°C)"},
)
st.plotly_chart(fig_timeline, use_container_width=True)
