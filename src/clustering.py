# src/clustering.py

import numpy as np
from sklearn.cluster import KMeans

def kmeans_clusters(
    X: np.ndarray,
    n_clusters: int = 4,
    random_state: int = 42,
):
    model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init="auto"
    )
    labels = model.fit_predict(X)
    return model, labels
