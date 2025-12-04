# app/pages/4_DimensionalityReduction.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from src.db_utils import get_engine

st.set_page_config(
    page_title="Dimensionality Reduction",
    page_icon="🧬",
    layout="wide",
)

@st.cache_data(show_spinner=False)
def load_embeddings():
    engine = get_engine()
    q = """
        SELECT e.*, d.season, d.total_rain, d.mean_temp, d.mean_wind_speed
        FROM weather_embeddings e
        JOIN weather_daily d ON e.date = d.date
        ORDER BY e.date
    """
    df = pd.read_sql(text(q), engine, parse_dates=["date"])
    return df

st.title("🧬 Dimensionality Reduction: PCA, t-SNE, UMAP")

df = load_embeddings()
if df.empty:
    st.warning("No embeddings found. Run etl_build_embeddings.py first.")
    st.stop()

with st.sidebar:
    st.header("View settings")
    method = st.selectbox("Method", ["PCA", "t-SNE", "UMAP"])
    color_by = st.selectbox(
        "Color by",
        ["season", "cluster_kmeans", "extreme_label", "total_rain", "mean_temp", "mean_wind_speed"],
    )
    size_by = st.selectbox(
        "Size by",
        ["None", "total_rain", "mean_wind_speed"],
    )

# chọn cặp chiều
if method == "PCA":
    x_col, y_col = "pca1", "pca2"
elif method == "t-SNE":
    x_col, y_col = "tsne1", "tsne2"
else:
    x_col, y_col = "umap1", "umap2"

color_arg = color_by
size_arg = None if size_by == "None" else size_by

st.subheader(f"{method} embedding")

fig = px.scatter(
    df,
    x=x_col,
    y=y_col,
    color=color_arg,
    size=size_arg,
    hover_data=["date", "season", "total_rain", "mean_temp", "mean_wind_speed", "extreme_label"],
    title=f"{method} 2D embedding colored by {color_by}",
)
st.plotly_chart(fig, use_container_width=True)

# timeline of chosen cluster/extreme label
st.subheader("Timeline of clusters / labels")

timeline_color_by = st.selectbox(
    "Timeline color by",
    ["cluster_kmeans", "extreme_label", "season"],
    index=0,
)

fig_t = px.scatter(
    df,
    x="date",
    y="mean_temp",
    color=timeline_color_by,
    size="total_rain",
    labels={"mean_temp": "Mean Temp (°C)"},
    title="Daily mean temperature timeline (size = rain, color = selected label)",
)
st.plotly_chart(fig_t, use_container_width=True)
