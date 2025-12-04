-- db/schema.sql
-- OPTION 1: tất cả attributes của Bradford Weather Data là cột

---------------------------------------------------------
-- BẢNG 1: RAW 30-MIN DATA
---------------------------------------------------------

CREATE TABLE IF NOT EXISTS weather_raw (
    id              SERIAL PRIMARY KEY,

    -- Thời gian & thông tin thời gian
    timestamp       TIMESTAMP NOT NULL,
    date            DATE NOT NULL,
    year            INT NOT NULL,
    month           INT NOT NULL,
    day             INT NOT NULL,
    hour            INT NOT NULL,
    season          VARCHAR(10),

    -- Ngoài trời (outdoor)
    temp_out        REAL,        -- Temp_Out
    hi_temp         REAL,        -- Hi_Temp
    low_temp        REAL,        -- Low_Temp
    out_hum         REAL,        -- Out_Hum
    dew_pt          REAL,        -- Dew_Pt

    wind_speed      REAL,        -- Wind_Speed
    wind_dir        VARCHAR(16), -- Wind_Dir (có '---')
    wind_run        REAL,        -- Wind_Run
    hi_speed        REAL,        -- Hi_Speed
    hi_dir          REAL,        -- Hi_Dir

    wind_chill      REAL,        -- Wind_Chill
    heat_index      REAL,        -- Heat_Index
    thw_index       REAL,        -- THW_Index
    thsw_index      REAL,        -- THSW_Index

    bar             REAL,        -- Bar␣␣ (áp suất)
    rain            REAL,        -- Rain (mm trong interval)
    rain_rate       REAL,        -- Rain_Rate (mm/h)

    solar_rad       REAL,        -- Solar_Rad
    solar_energy    REAL,        -- Solar_Energy
    hi_solar_rad    REAL,        -- Hi Solar_Rad

    uv_index        REAL,        -- UV_Index
    uv_dose         REAL,        -- UV_Dose
    hi_uv           REAL,        -- Hi_UV

    heat_dd         REAL,        -- Heat_D-D
    cool_dd         REAL,        -- Cool_D-D

    -- Indoor
    in_temp         REAL,        -- In_Temp
    in_hum          REAL,        -- In_Hum
    in_dew          REAL,        -- In_Dew
    in_heat         REAL,        -- In_Heat
    in_emc          REAL,        -- In_EMC
    in_air_density  REAL,        -- InAir_Density

    et              REAL,        -- ET␣
    wind_samp       REAL,        -- Wind_Samp
    wind_tx         REAL,        -- Wind_Tx
    iss_recept      REAL,        -- ISS_Recept
    arc_int         REAL         -- Arc_Int
);

CREATE INDEX IF NOT EXISTS idx_weather_raw_timestamp
    ON weather_raw (timestamp);

CREATE INDEX IF NOT EXISTS idx_weather_raw_date
    ON weather_raw (date);

CREATE INDEX IF NOT EXISTS idx_weather_raw_season
    ON weather_raw (season);


---------------------------------------------------------
-- BẢNG 2: DAILY AGGREGATED FEATURES
---------------------------------------------------------

CREATE TABLE IF NOT EXISTS weather_daily (
    date            DATE PRIMARY KEY,
    year            INT NOT NULL,
    month           INT NOT NULL,
    season          VARCHAR(10),

    mean_temp       REAL,
    max_temp        REAL,
    min_temp        REAL,
    temp_range      REAL,

    mean_humidity   REAL,
    humidity_range  REAL,

    total_rain      REAL,
    mean_wind_speed REAL,
    max_wind_speed  REAL,

    mean_pressure   REAL,
    pressure_range  REAL,

    mean_solar      REAL,

    rain_flag       BOOLEAN,
    wind_flag       BOOLEAN
);


---------------------------------------------------------
-- BẢNG 3: EMBEDDINGS (PCA, t-SNE, UMAP, CLUSTERS)
---------------------------------------------------------

CREATE TABLE IF NOT EXISTS weather_embeddings (
    date            DATE PRIMARY KEY REFERENCES weather_daily(date),

    -- PCA
    pca1            REAL,
    pca2            REAL,
    pca3            REAL,

    -- t-SNE
    tsne1           REAL,
    tsne2           REAL,

    -- UMAP
    umap1           REAL,
    umap2           REAL,

    -- Clustering
    cluster_kmeans  INT,
    extreme_label   VARCHAR(32)
);
