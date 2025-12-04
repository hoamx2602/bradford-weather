# db/etl_build_daily.py

import pandas as pd
from sqlalchemy import text
from src.db_utils import get_engine
from src.preprocessing import aggregate_daily, label_extremes

def main():
    engine = get_engine()

    # Load từ weather_raw với các cột cần thiết
    query = """
        SELECT
          timestamp, date, year, month, season,
          temp_out, out_hum, wind_speed,
          bar, solar_rad, rain
        FROM weather_raw
        WHERE timestamp IS NOT NULL;
    """
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])

    daily = aggregate_daily(df)
    daily = label_extremes(daily)

    with engine.begin() as conn:
        # CASCADE để truncate cả weather_embeddings (có FK reference)
        conn.execute(text("TRUNCATE TABLE weather_daily CASCADE;"))
    daily.to_sql("weather_daily", engine, if_exists="append", index=False)

    print(f"Inserted {len(daily)} rows into weather_daily")

if __name__ == "__main__":
    main()
