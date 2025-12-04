# src/dim_reduction.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

DEFAULT_FEATURES = [
    "mean_temp", "temp_range",
    "mean_humidity", "humidity_range",
    "total_rain",
    "mean_wind_speed", "max_wind_speed",
    "mean_pressure", "pressure_range",
    "mean_solar",
]

def prepare_matrix(daily: pd.DataFrame,
                   feature_cols: list[str] | None = None):
    if feature_cols is None:
        feature_cols = DEFAULT_FEATURES
    X = daily[feature_cols].copy()
    
    # Xử lý NaN: drop rows có NaN trong bất kỳ feature nào
    # (vì PCA/t-SNE/UMAP không chấp nhận NaN)
    valid_mask = ~X.isna().any(axis=1)
    X_clean = X[valid_mask].copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)
    return X_scaled, feature_cols, scaler, valid_mask

def run_pca(X_scaled: np.ndarray, n_components: int = 3):
    pca = PCA(n_components=n_components, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    return pca, X_pca

def run_tsne(X_scaled: np.ndarray,
             n_components: int = 2,
             perplexity: float = 30.0,
             random_state: int = 42):
    tsne = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        random_state=random_state,
        init="pca",
        learning_rate="auto"
    )
    X_tsne = tsne.fit_transform(X_scaled)
    return tsne, X_tsne

def run_umap(X_scaled: np.ndarray,
             n_components: int = 2,
             random_state: int = 42,
             n_neighbors: int = 15,
             min_dist: float = 0.1):
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        random_state=random_state,
    )
    X_umap = reducer.fit_transform(X_scaled)
    return reducer, X_umap
