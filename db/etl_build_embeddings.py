# db/etl_build_embeddings.py

import pandas as pd
from sqlalchemy import text
from src.db_utils import get_engine
from src.dim_reduction import prepare_matrix, run_pca, run_tsne, run_umap
from src.clustering import kmeans_clusters

def main():
    engine = get_engine()

    daily = pd.read_sql("SELECT * FROM weather_daily ORDER BY date;", engine)

    X_scaled, features, scaler, valid_mask = prepare_matrix(daily)
    
    # Chỉ giữ các rows không có NaN
    daily_clean = daily[valid_mask].reset_index(drop=True)
    
    n_dropped = (~valid_mask).sum()
    if n_dropped > 0:
        print(f"Warning: Dropped {n_dropped} rows with NaN values (out of {len(daily)} total)")
    print(f"Processing {len(daily_clean)} rows for embeddings")

    # PCA
    pca, X_pca = run_pca(X_scaled, n_components=3)

    # t-SNE
    _, X_tsne = run_tsne(X_scaled, n_components=2, perplexity=30.0)

    # UMAP
    _, X_umap = run_umap(X_scaled, n_components=2)

    # Clustering trên PCA (hoặc X_scaled)
    _, labels = kmeans_clusters(X_pca[:, :2], n_clusters=4)

    emb = pd.DataFrame({
        "date": daily_clean["date"],
        "pca1": X_pca[:, 0],
        "pca2": X_pca[:, 1],
        "pca3": X_pca[:, 2],
        "tsne1": X_tsne[:, 0],
        "tsne2": X_tsne[:, 1],
        "umap1": X_umap[:, 0],
        "umap2": X_umap[:, 1],
        "cluster_kmeans": labels,
    })

    # extreme_label (optional)
    def label_row(row):
        if row["rain_flag"]:
            return "heavy_rain"
        if row["wind_flag"]:
            return "strong_wind"
        return "normal"

    daily_flags = daily_clean[["date", "rain_flag", "wind_flag"]].copy()
    emb = emb.merge(daily_flags, on="date", how="left")
    emb["extreme_label"] = emb.apply(label_row, axis=1)

    # Drop helper flags before insert
    emb_to_db = emb[[
        "date", "pca1", "pca2", "pca3",
        "tsne1", "tsne2",
        "umap1", "umap2",
        "cluster_kmeans", "extreme_label"
    ]]

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE weather_embeddings;"))
    emb_to_db.to_sql("weather_embeddings", engine, if_exists="append", index=False)

    print(f"Inserted {len(emb_to_db)} rows into weather_embeddings")

if __name__ == "__main__":
    main()
