# app/pages/3_MultivariateAnalysis.py

import sys
from pathlib import Path

# Add project root to Python path for Streamlit Cloud
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import text
from pandas.plotting import andrews_curves
import matplotlib.pyplot as plt

from src.db_utils import get_engine

st.set_page_config(
    page_title="Multivariate Analysis",
    page_icon="📐",
    layout="wide",
)

@st.cache_data(show_spinner=False)
def load_daily(date_from=None, date_to=None, season=None):
    engine = get_engine()
    base = "SELECT * FROM weather_daily WHERE 1=1"
    params = {}
    if date_from:
        base += " AND date >= :date_from"
        params["date_from"] = date_from
    if date_to:
        base += " AND date <= :date_to"
        params["date_to"] = date_to
    if season and season != "All":
        base += " AND season = :season"
        params["season"] = season
    base += " ORDER BY date"
    df = pd.read_sql(text(base), engine, params=params, parse_dates=["date"])
    return df

st.title("📐 Multivariate Analysis")

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input("Date range", [])
    season = st.selectbox("Season", ["All", "Winter", "Spring", "Summer", "Autumn"])

if len(date_range) == 2:
    df = load_daily(date_from=date_range[0], date_to=date_range[1], season=season)
else:
    df = load_daily(season=season)

if df.empty:
    st.warning("No data for selected filters.")
    st.stop()

numeric_cols = [
    "mean_temp", "max_temp", "min_temp",
    "mean_humidity", "humidity_range",
    "total_rain",
    "mean_wind_speed", "max_wind_speed",
    "mean_pressure", "pressure_range",
    "mean_solar",
]

df_num = df[numeric_cols].copy()

# --- Correlation heatmap ---
st.subheader("Correlation Heatmap")

corr = df_num.corr()

fig_corr = px.imshow(
    corr,
    x=corr.columns,
    y=corr.columns,
    color_continuous_scale="RdBu",
    zmin=-1,
    zmax=1,
    title="Correlation matrix between daily features",
)
st.plotly_chart(fig_corr, use_container_width=True)

# --- Scatter explorer ---
st.subheader("Bivariate Scatter Explorer")

c1, c2, c3 = st.columns(3)
with c1:
    x_var = st.selectbox("X variable", numeric_cols, index=0)
with c2:
    y_var = st.selectbox("Y variable", numeric_cols, index=3)
with c3:
    color_by = st.selectbox(
        "Color by",
        ["None", "season", "total_rain", "mean_wind_speed", "rain_flag", "wind_flag"],
        index=1,
    )

df_plot = df.copy()
color_arg = None if color_by == "None" else color_by

fig_scatter = px.scatter(
    df_plot,
    x=x_var,
    y=y_var,
    color=color_arg,
    hover_data=["date"],
    labels={"date": "Date"},
    title=f"{x_var} vs {y_var}",
)
st.plotly_chart(fig_scatter, use_container_width=True)

# --- Parallel coordinates ---
st.subheader("Parallel Coordinates (sampled)")

sample_size = st.slider("Sample size", min_value=50, max_value=min(500, len(df)), value=min(200, len(df)))
df_sample = df.sample(n=sample_size, random_state=42) if len(df) > sample_size else df.copy()

cols_parallel = st.multiselect(
    "Variables for parallel coordinates",
    numeric_cols,
    default=["mean_temp", "mean_humidity", "total_rain", "mean_wind_speed", "mean_pressure"],
)

if len(cols_parallel) >= 2:
    df_par = df_sample[cols_parallel + ["season"]].copy()
    
    # Map season to numeric values for color mapping (0-3)
    season_map = {"Spring": 0, "Summer": 1, "Autumn": 2, "Winter": 3}
    df_par["season_numeric"] = df_par["season"].map(season_map)
    
    # Use numeric column for color with discrete color scale
    fig_par = px.parallel_coordinates(
        df_par,
        color="season_numeric",
        color_continuous_scale=[[0, "#2ecc71"], [0.33, "#e74c3c"], [0.67, "#f39c12"], [1, "#3498db"]],  # Spring, Summer, Autumn, Winter
        labels={c: c for c in cols_parallel},
        title="Parallel coordinates of selected features (colored by season)",
    )
    
    # Update colorbar to show season labels
    fig_par.update_layout(
        coloraxis=dict(
            colorbar=dict(
                tickvals=[0, 1, 2, 3],
                ticktext=["Spring", "Summer", "Autumn", "Winter"],
                title="Season",
                lenmode="fraction",
                len=0.5,
            ),
            cmin=-0.5,
            cmax=3.5,
        )
    )
    
    st.plotly_chart(fig_par, use_container_width=True)
else:
    st.info("Select at least two variables for parallel coordinates.")

# --- Andrews curves ---
st.subheader("Andrews Curves (Pandas plotting)")

st.markdown(
    "Each curve represents a day, constructed from multiple features; "
    "similar curve shapes suggest similar multivariate profiles."
)

# Chuẩn bị DataFrame phù hợp cho andrews_curves: numeric + class column
andrews_cols_default = ["mean_temp", "mean_humidity", "total_rain", "mean_wind_speed", "mean_pressure", "mean_solar"]
andrews_cols = [c for c in andrews_cols_default if c in df.columns]

if len(andrews_cols) >= 3:
    df_andrews = df[andrews_cols + ["season"]].dropna().copy()
    # Giới hạn số points để plot không quá nặng
    max_curves = st.slider("Max number of curves", 50, 400, 200)
    if len(df_andrews) > max_curves:
        df_andrews = df_andrews.sample(n=max_curves, random_state=42)

    fig, ax = plt.subplots(figsize=(8, 4))
    andrews_curves(df_andrews, "season", ax=ax)
    ax.set_title("Andrews curves grouped by season")
    st.pyplot(fig)
else:
    st.info("Not enough numeric columns available for Andrews curves.")
