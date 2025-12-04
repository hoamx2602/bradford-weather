# app/pages/2_TimeSeriesExplorer.py

import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
from src.db_utils import get_engine

st.set_page_config(page_title="Time Series Explorer", page_icon="⏱️", layout="wide")

@st.cache_data(show_spinner=False)
def load_raw(date_from=None, date_to=None):
    engine = get_engine()
    base = """
        SELECT timestamp, date,
               temp_out, out_hum,
               wind_speed, bar, solar_rad, rain_rate
        FROM weather_raw
        WHERE timestamp IS NOT NULL
    """
    params = {}
    if date_from:
        base += " AND date >= :date_from"
        params["date_from"] = date_from
    if date_to:
        base += " AND date <= :date_to"
        params["date_to"] = date_to
    base += " ORDER BY timestamp"
    df = pd.read_sql(text(base), engine, params=params, parse_dates=["timestamp", "date"])
    return df

st.title("⏱️ Time Series Explorer")

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input("Date range", [])
    variables = st.multiselect(
        "Variables",
        ["temp_out", "out_hum", "wind_speed", "bar", "solar_rad", "rain_rate"],
        default=["temp_out", "rain_rate"],
    )
    agg_level = st.selectbox("Aggregation", ["Raw (30-min)", "Hourly", "Daily"])

if len(date_range) == 2:
    df_raw = load_raw(date_from=date_range[0], date_to=date_range[1])
else:
    df_raw = load_raw()

if df_raw.empty:
    st.warning("No data for selected filters.")
    st.stop()

df_plot = df_raw.copy()
if agg_level == "Hourly":
    df_plot = (
        df_plot
        .set_index("timestamp")
        .resample("1H")
        .mean()
        .reset_index()
    )
elif agg_level == "Daily":
    df_plot = (
        df_plot
        .set_index("timestamp")
        .resample("1D")
        .mean()
        .reset_index()
    )

st.subheader("Selected Time Series")

for var in variables:
    fig = px.line(
        df_plot,
        x="timestamp",
        y=var,
        title=var,
        labels={"timestamp": "Time", var: var},
    )
    st.plotly_chart(fig, use_container_width=True)
