# db/etl_load_raw.py

import pandas as pd
from sqlalchemy import text
from src.db_utils import get_engine, execute_sql_file
from src.preprocessing import parse_timestamp, clean_numeric
from src.constants import PROJECT_ROOT

RAW_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "Bradford_Weather_Data.csv"
SCHEMA_SQL_PATH = PROJECT_ROOT / "db" / "schema.sql"

# Tất cả cột numeric (mọi thứ trừ Date, Time, Wind_Dir)
NUMERIC_COLS = [
    "Temp_Out", "Hi_Temp", "Low_Temp",
    "Out_Hum", "Dew_Pt",
    "Wind_Speed", "Wind_Run", "Hi_Speed", "Hi_Dir",
    "Wind_Chill", "Heat_Index", "THW_Index", "THSW_Index",
    "Bar  ", "Rain", "Rain_Rate",
    "Solar_Rad", "Solar_Energy", "Hi Solar_Rad",
    "UV_Index", "UV_Dose", "Hi_UV",
    "Heat_D-D", "Cool_D-D",
    "In_Temp", "In_Hum", "In_Dew", "In_Heat", "In_EMC", "InAir_Density",
    "ET ", "Wind_Samp", "Wind_Tx", "ISS_Recept", "Arc_Int",
]

def main():
    engine = get_engine()

    # Tạo schema
    execute_sql_file(engine, str(SCHEMA_SQL_PATH))

    # Load CSV
    df = pd.read_csv(RAW_CSV_PATH)

    # Parse timestamp + thêm year/month/day/hour/season
    df = parse_timestamp(df, date_col="Date", time_col="Time")
    df = clean_numeric(df, NUMERIC_COLS)

    # Chuẩn hoá tên cột theo schema
    rename_map = {
        "Temp_Out": "temp_out",
        "Hi_Temp": "hi_temp",
        "Low_Temp": "low_temp",
        "Out_Hum": "out_hum",
        "Dew_Pt": "dew_pt",

        "Wind_Speed": "wind_speed",
        "Wind_Dir": "wind_dir",
        "Wind_Run": "wind_run",
        "Hi_Speed": "hi_speed",
        "Hi_Dir": "hi_dir",

        "Wind_Chill": "wind_chill",
        "Heat_Index": "heat_index",
        "THW_Index": "thw_index",
        "THSW_Index": "thsw_index",

        "Bar  ": "bar",
        "Rain": "rain",
        "Rain_Rate": "rain_rate",

        "Solar_Rad": "solar_rad",
        "Solar_Energy": "solar_energy",
        "Hi Solar_Rad": "hi_solar_rad",

        "UV_Index": "uv_index",
        "UV_Dose": "uv_dose",
        "Hi_UV": "hi_uv",

        "Heat_D-D": "heat_dd",
        "Cool_D-D": "cool_dd",

        "In_Temp": "in_temp",
        "In_Hum": "in_hum",
        "In_Dew": "in_dew",
        "In_Heat": "in_heat",
        "In_EMC": "in_emc",
        "InAir_Density": "in_air_density",

        "ET ": "et",
        "Wind_Samp": "wind_samp",
        "Wind_Tx": "wind_tx",
        "ISS_Recept": "iss_recept",
        "Arc_Int": "arc_int",
    }
    df = df.rename(columns=rename_map)

    # Chọn đúng thứ sẽ insert vào weather_raw
    cols_order = [
        "timestamp", "date", "year", "month", "day", "hour", "season",
        "temp_out", "hi_temp", "low_temp",
        "out_hum", "dew_pt",
        "wind_speed", "wind_dir", "wind_run", "hi_speed", "hi_dir",
        "wind_chill", "heat_index", "thw_index", "thsw_index",
        "bar", "rain", "rain_rate",
        "solar_rad", "solar_energy", "hi_solar_rad",
        "uv_index", "uv_dose", "hi_uv",
        "heat_dd", "cool_dd",
        "in_temp", "in_hum", "in_dew", "in_heat", "in_emc", "in_air_density",
        "et", "wind_samp", "wind_tx", "iss_recept", "arc_int",
    ]
    df = df[cols_order]

    # Đổ vào DB
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE weather_raw RESTART IDENTITY;"))
    df.to_sql("weather_raw", engine, if_exists="append", index=False)

    print(f"Inserted {len(df)} rows into weather_raw")

if __name__ == "__main__":
    main()
