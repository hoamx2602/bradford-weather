# app/pages/5_WeatherRegimes.py

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
import plotly.graph_objects as go
from sqlalchemy import text

from src.db_utils import get_engine

st.set_page_config(
    page_title="Weather Regimes",
    page_icon="🌐",
    layout="wide",
)

@st.cache_data(show_spinner=False)
def load_regimes():
    engine = get_engine()
    q = """
        SELECT e.date, e.cluster_kmeans, e.extreme_label,
               d.season, d.total_rain, d.mean_temp, d.mean_humidity,
               d.mean_wind_speed, d.max_wind_speed, d.mean_pressure,
               d.mean_solar, d.temp_range, d.humidity_range
        FROM weather_embeddings e
        JOIN weather_daily d ON e.date = d.date
        ORDER BY e.date
    """
    df = pd.read_sql(text(q), engine, parse_dates=["date"])
    return df

st.title("🌐 Weather Regimes (Clusters)")

df = load_regimes()
if df.empty:
    st.warning("No regime data. Run etl_build_embeddings.py first.")
    st.stop()

df["cluster_kmeans"] = df["cluster_kmeans"].astype(int)
cluster_ids = sorted(df["cluster_kmeans"].unique())

with st.sidebar:
    st.header("Filters")
    cluster_sel = st.multiselect(
        "Select clusters",
        cluster_ids,
        default=cluster_ids,
    )
    season_sel = st.multiselect(
        "Seasons",
        ["Winter", "Spring", "Summer", "Autumn"],
        default=["Winter", "Spring", "Summer", "Autumn"],
    )

mask = df["cluster_kmeans"].isin(cluster_sel) & df["season"].isin(season_sel)
df_f = df[mask].copy()

if df_f.empty:
    st.warning("No data for selected filters.")
    st.stop()

# --- Summary table ---
st.subheader("Regime summary")

summary = (
    df_f
    .groupby("cluster_kmeans")
    .agg(
        n_days=("date", "nunique"),
        mean_temp=("mean_temp", "mean"),
        total_rain=("total_rain", "mean"),
        mean_wind=("mean_wind_speed", "mean"),
        extreme_days=("extreme_label", lambda x: (x != "normal").sum()),
    )
    .reset_index()
)

summary["extreme_ratio"] = summary["extreme_days"] / summary["n_days"]

st.dataframe(summary.style.format({
    "mean_temp": "{:.1f}",
    "total_rain": "{:.1f}",
    "mean_wind": "{:.1f}",
    "extreme_ratio": "{:.2f}",
}))

# --- PCA-like scatter with clusters (reuse pca from embeddings table) ---
st.subheader("Regimes in PCA space")

# load PCA coordinates
engine = get_engine()
df_pca = pd.read_sql(
    text("""
        SELECT e.date, e.cluster_kmeans, d.season,
               e.pca1, e.pca2
        FROM weather_embeddings e
        JOIN weather_daily d ON e.date = d.date
        ORDER BY e.date
    """),
    engine,
    parse_dates=["date"],
)

df_pca["cluster_kmeans"] = df_pca["cluster_kmeans"].astype(int)
df_pca = df_pca[
    df_pca["cluster_kmeans"].isin(cluster_sel)
    & df_pca["season"].isin(season_sel)
]

fig_sc = px.scatter(
    df_pca,
    x="pca1",
    y="pca2",
    color="cluster_kmeans",
    symbol="season",
    hover_data=["date"],
    title="Weather regimes in PCA space",
)
st.plotly_chart(fig_sc, use_container_width=True)

# --- Radar plot per cluster ---
st.subheader("Cluster profiles (Radar)")

# chọn cluster cho radar
cluster_for_radar = st.selectbox(
    "Select cluster for radar profile",
    cluster_ids,
)

features_for_radar = [
    "mean_temp",
    "mean_humidity",
    "total_rain",
    "mean_wind_speed",
    "mean_pressure",
    "mean_solar",
]

df_centroids = (
    df.groupby("cluster_kmeans")[features_for_radar]
    .mean()
)

# chuẩn hóa 0-1 để radar dễ đọc
radar_norm = (df_centroids - df_centroids.min()) / (df_centroids.max() - df_centroids.min())
radar_norm = radar_norm.fillna(0)

fig_radar = go.Figure()

for cid in cluster_ids:
    r_vals = radar_norm.loc[cid, features_for_radar].values.tolist()
    # đóng vòng
    r_vals += r_vals[:1]
    theta = features_for_radar + [features_for_radar[0]]
    fig_radar.add_trace(go.Scatterpolar(
        r=r_vals,
        theta=theta,
        name=f"Cluster {cid}",
        visible=(cid == cluster_for_radar)  # chỉ show 1 cluster mặc định
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 1]),
    ),
    showlegend=True,
    title="Normalized feature profile for selected cluster",
)

# bật chỉ cluster được chọn
for i, cid in enumerate(cluster_ids):
    fig_radar.data[i].visible = (cid == cluster_for_radar)

st.plotly_chart(fig_radar, use_container_width=True)

# --- Cluster composition over time ---
st.subheader("Cluster distribution by month")

df_month = (
    df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
    .groupby(["month", "cluster_kmeans"])
    .size()
    .reset_index(name="n_days")
)

fig_month = px.bar(
    df_month,
    x="month",
    y="n_days",
    color="cluster_kmeans",
    title="Number of days per regime over months",
)
st.plotly_chart(fig_month, use_container_width=True)
