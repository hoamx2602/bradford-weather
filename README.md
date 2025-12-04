# 🌤️ Bradford Weather Analytics

### Big Data & Visualisation Coursework – Full Stack Analytics & Interactive Dashboard

This project is a full-stack data analytics system built for the **Bradford Weather Station dataset**, containing high-resolution meteorological measurements (30-minute intervals).
The system ingests raw CSV data, loads & cleans it, aggregates daily features, generates embeddings (PCA, t-SNE, UMAP), performs exploratory analysis, and provides a fully interactive Streamlit dashboard for visualisation.

---

## 🚀 1. Project Structure

```
.
├── app/
│   ├── Home.py
│   └── pages/
│        ├── 0_DailyWeatherCard.py
│        ├── 1_Overview.py
│        ├── 2_Daily_Explorer.py
│        ├── 3_Seasonality.py
│        ├── 4_Embeddings.py
│        └── 5_Trends.py
│
├── data/
│   ├── raw/
│   │     └── Bradford_Weather_Data.csv
│   └── processed/
│         ├── daily.parquet
│         ├── embeddings.parquet
│         └── hourly_sample.parquet
│
├── db/
│   ├── schema.sql
│   ├── etl_load_raw.py
│   ├── etl_build_daily.py
│   └── etl_build_embeddings.py
│
├── notebooks/
│   ├── EDA.ipynb
│   ├── PCA_tsne_umap.ipynb
│   └── FeatureSelection.ipynb
│
├── src/
│   ├── constants.py
│   ├── db_utils.py
│   ├── preprocessing.py
│   ├── embedding.py
│   └── utils.py
│
└── README.md
```

---

## 📦 2. Features & Capabilities

### 🔹 **Full ETL Pipeline**

* Parse, clean & normalise all raw weather attributes
* Convert timestamps, derive hour/day/month/year/season
* Validate and clean numeric attributes
* Store all data in **PostgreSQL** with a fully expanded schema (Option 1)

### 🔹 **Daily Aggregation Engine**

Creates a `weather_daily` table summarising:

* Mean/Max/Min temperatures
* Humidity
* Rainfall totals
* Wind metrics
* Pressure ranges
* Solar radiation mean

### 🔹 **Embeddings & Machine Learning**

Generated in `weather_embeddings` table:

* PCA (PC1, PC2, PC3)
* t-SNE (dim1, dim2)
* UMAP (dim1, dim2)
* KMeans clustering labels
* Classification into **Extreme Weather Regimes**

These embeddings power advanced visualisations in Streamlit.

---

## 🎨 3. Interactive Streamlit Dashboard

### 🔸 **Home**

* Explains system architecture & dataset
* Navigation hub for all modules

### 🔸 **Daily Weather Card (0_DailyWeatherCard)**

Interactive UI similar to modern weather apps:

* Select any date
* Shows temperature, wind, rain, pressure, condition icon
* 6-day forecast
* Stylish card with gradient and icons

### 🔸 **Overview Dashboard (1_Overview)**

A polished, professional analytics page featuring:

* Today card
* Temperature gauge
* Humidity gauge
* Wind summary
* Hourly temperature & rainfall charts
* Highlights (rain, pressure, wind, humidity)
* Calendar heatmap for temperature

### 🔸 **Daily Explorer**

Line charts, bar charts, rain accumulation, hourly patterns.

### 🔸 **Seasonality Analysis**

Trends by:

* Month
* Season
* Year-over-year comparison
* Temperature distribution
* Rainfall seasonality

### 🔸 **Embeddings Explorer**

Interactive 2D visualisations:

* PCA scatter
* t-SNE
* UMAP
* Cluster colouring
* Extreme weather anomaly detection

### 🔸 **Trends & Long-term Changes**

* Smoothed LOESS curves
* Multi-year changes
* Rolling averages
* Extreme temperature trends

---

## 🛠️ 4. Installation & Setup

### 1️⃣ **Create environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ **Configure PostgreSQL**

Create database:

```sql
CREATE DATABASE weather;
```

Update credentials in `.env`:

```
DB_HOST=...
DB_PORT=5432
DB_USER=...
DB_PASS=...
DB_NAME=weather
```

### 3️⃣ **Load schema**

```bash
python db/etl_load_raw.py
```

### 4️⃣ **Build daily table**

```bash
python db/etl_build_daily.py
```

### 5️⃣ **Generate embeddings**

```bash
python db/etl_build_embeddings.py
```

### 6️⃣ **Run Streamlit**

```bash
cd app
streamlit run Home.py
```

---

## 📊 5. Data Pipeline Diagram

**Raw CSV → ETL → PostgreSQL → Daily Aggregates → Embeddings → Dashboard**

```
Bradford_Weather_Data.csv
        ↓ (parse + clean)
      weather_raw (Postgres)
        ↓ (aggregate_daily)
      weather_daily
        ↓ (PCA / t-SNE / UMAP / clustering)
      weather_embeddings
        ↓
        DASHBOARD (Streamlit)
```

---

## 🧠 6. Machine Learning & Feature Engineering

### PCA

* Used to reduce dimensionality & understand major variance sources
* Helps identify temperature-driven, humidity-driven, or radiation-driven behaviours

### t-SNE

* Explores nonlinear relationships
* Reveals potential clusters of similar weather days

### UMAP

* Better structural preservation for high-dimensional patterns
* Used to identify weather “regimes”

### KMeans

* Groups days into clusters
* Used for labeling “extreme”, “dry”, “wet”, “cold”, “mixed” days

Results visualised directly on dashboard.

---

## 📝 7. Coursework Report (How to write)

The report should include:

### ✔️ Introduction

* Dataset description
* Motivation & context

### ✔️ ETL & System Architecture

* Diagram
* Decisions on schema (Option 1: full denormalisation)

### ✔️ Exploratory Data Analysis

* Patterns
* Outliers
* Correlations

### ✔️ Seasonality & Trends

* Monthly and seasonal effects
* Temperature trends
* Rain distribution

### ✔️ Dimensionality Reduction

* PCA interpretation (PC loadings, variance explained)
* t-SNE & UMAP visual clusters
* Weather regime analysis

### ✔️ Dashboard Design

* UX/UI decisions
* Interactivity
* Visual storytelling

### ✔️ Conclusion

* Key findings
* Limitations
* Future improvements

---

## 👨‍💻 8. Tech Stack

| Component           | Technology                 |
| ------------------- | -------------------------- |
| **Database**        | PostgreSQL                 |
| **Backend ETL**     | Python, Pandas, SQLAlchemy |
| **ML / Embeddings** | Scikit-learn, UMAP-learn   |
| **Visualisation**   | Streamlit, Plotly, Seaborn |
| **Deployment**      | Streamlit Cloud            |
| **Version Control** | GitHub Repo                |

---

## 🎯 9. Learning Outcomes (Matches BDV module)

* Hands-on ETL & data pipeline construction
* Handling real-world environmental datasets
* Dimensionality reduction (PCA, t-SNE, UMAP)
* Feature engineering
* Interactive analytics dashboard design
* Professional data storytelling

---

## 📬 10. Contact