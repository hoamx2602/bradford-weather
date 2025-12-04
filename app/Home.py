# app/Home.py

import streamlit as st

st.set_page_config(
    page_title="Bradford Weather Analytics",
    page_icon="🌦️",
    layout="wide",
)

st.title("🌦️ Bradford Weather Analytics Dashboard")
st.markdown("""
Welcome to the **Bradford Weather Analytics** dashboard.

Use the navigation on the left to explore:

1. **Overview** – high-level KPIs & calendar view  
2. **Time Series Explorer** – zoom into specific periods & variables  
3. **Multivariate Analysis** – correlations & relationships  
4. **Dimensionality Reduction** – PCA, t-SNE, UMAP embeddings  
5. **Weather Regimes** – discovered clusters of typical weather days  
6. **Extreme Events** – storms, heavy rain, strong wind episodes  
""")
