import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").strip().lower()
_sqlite_raw = Path(os.getenv("SQLITE_PATH", "data/ragdb.sqlite"))
SQLITE_PATH = _sqlite_raw if _sqlite_raw.is_absolute() else PROJECT_ROOT / _sqlite_raw


def get_db_config() -> Dict[str, Any]:
    if DB_BACKEND == "postgres":
        return {
            "backend": "postgres",
            "dbname": os.getenv("DB_NAME", "ragdb"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "yourpassword"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return {
        "backend": "sqlite",
        "path": str(SQLITE_PATH.resolve()),
    }


def sql_dialect() -> str:
    return "postgres" if DB_BACKEND == "postgres" else "sqlite"


def connect_sqlite(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def connect_postgres(cfg: Dict[str, Any]):
    import psycopg2

    return psycopg2.connect(
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"],
    )


def execute_query(sql: str, params: Optional[List[Any]] = None) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    cfg = get_db_config()
    params = params or []
    try:
        if cfg["backend"] == "sqlite":
            conn = connect_sqlite(cfg["path"])
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]
            cur.close()
            conn.close()
            return rows, None

        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = connect_postgres(cfg)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return rows, None

    except Exception as e:
        return None, f"Database execution error: {e}"


def table_is_empty(table: str) -> bool:
    rows, err = execute_query(f"SELECT COUNT(*) AS n FROM {table};", [])
    if err or not rows:
        return True
    return int(rows[0].get("n", 0)) == 0
