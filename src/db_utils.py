# src/db_utils.py

import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()

def get_db_url() -> str:
    """
    Đọc DATABASE_URL từ .env
    Ví dụ: postgresql+psycopg2://user:password@host:5432/dbname
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Please set DATABASE_URL in your .env file")
    return url

def get_engine(echo: bool = False) -> Engine:
    """Create SQLAlchemy engine."""
    return create_engine(get_db_url(), echo=echo, future=True)

def execute_sql_file(engine: Engine, sql_path: str) -> None:
    """Run all statements in a .sql file (for schema creation)."""
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_text = f.read()
    with engine.begin() as conn:
        for stmt in sql_text.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))
