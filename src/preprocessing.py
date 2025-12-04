# src/preprocessing.py

import pandas as pd
import numpy as np
from .constants import SEASON_MAP

def parse_timestamp(df: pd.DataFrame, date_col: str, time_col: str) -> pd.DataFrame:
    ts = pd.to_datetime(df[date_col] + " " + df[time_col], dayfirst=True, errors="coerce")
    df = df.copy()
    df["timestamp"] = ts
    df["date"] = df["timestamp"].dt.date
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day
    df["hour"] = df["timestamp"].dt.hour
    df["season"] = df["month"].map(SEASON_MAP)
    return df

def clean_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    group = df.groupby("date")

    agg = pd.DataFrame({
        "year": group["year"].first(),
        "month": group["month"].first(),
        "season": group["season"].first(),

        "mean_temp": group["temp_out"].mean(),
        "max_temp": group["temp_out"].max(),
        "min_temp": group["temp_out"].min(),
        "temp_range": group["temp_out"].max() - group["temp_out"].min(),

        "mean_humidity": group["out_hum"].mean(),
        "humidity_range": group["out_hum"].max() - group["out_hum"].min(),

        "total_rain": group["rain"].sum(),

        "mean_wind_speed": group["wind_speed"].mean(),
        "max_wind_speed": group["wind_speed"].max(),

        "mean_pressure": group["bar"].mean(),
        "pressure_range": group["bar"].max() - group["bar"].min(),

        "mean_solar": group["solar_rad"].mean(),
    })

    agg.reset_index(inplace=True)
    return agg

def label_extremes(daily: pd.DataFrame,
                   rain_q: float = 0.95,
                   wind_q: float = 0.95) -> pd.DataFrame:
    daily = daily.copy()
    rain_thr = daily["total_rain"].quantile(rain_q)
    wind_thr = daily["max_wind_speed"].quantile(wind_q)

    daily["rain_flag"] = daily["total_rain"] >= rain_thr
    daily["wind_flag"] = daily["max_wind_speed"] >= wind_thr
    return daily
