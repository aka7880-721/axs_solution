"""Create schema and seed sample data if the database is empty."""

from pathlib import Path

from db.database import connect_sqlite, execute_query, get_db_config
from db import seed_data


def _sqlite_has_customers_table(path: str) -> bool:
    if not Path(path).exists():
        return False
    conn = connect_sqlite(path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers';")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row is not None


def _apply_schema_sqlite(path: str) -> None:
    schema_path = Path(__file__).parent / "schema_sqlite.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn = connect_sqlite(path)
    conn.executescript(sql)
    conn.commit()
    conn.close()


def _apply_schema_postgres(cfg: dict) -> None:
    from db.database import connect_postgres

    schema_path = Path(__file__).parent / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")
    conn = connect_postgres(cfg)
    cur = conn.cursor()
    for statement in (part.strip() for part in sql.split(";")):
        if statement:
            cur.execute(statement)
    conn.commit()
    cur.close()
    conn.close()


def _customer_count() -> int:
    rows, err = execute_query("SELECT COUNT(*) AS n FROM customers;", [])
    if err or not rows:
        return -1
    return int(rows[0].get("n", 0))


def ensure_database(force_seed: bool = False) -> None:
    cfg = get_db_config()
    needs_seed = force_seed

    if cfg["backend"] == "sqlite":
        Path(cfg["path"]).parent.mkdir(parents=True, exist_ok=True)
        if not Path(cfg["path"]).exists() or not _sqlite_has_customers_table(cfg["path"]):
            _apply_schema_sqlite(cfg["path"])
            needs_seed = True
        elif seed_data.get_seed_version() < seed_data.SEED_VERSION:
            needs_seed = True
    else:
        count = _customer_count()
        if count < 0:
            _apply_schema_postgres(cfg)
            needs_seed = True

    count = _customer_count()
    if needs_seed or count <= 0:
        seed_data.seed()
        print("Database ready (schema + sample data).")
    else:
        print("Database ready (existing data).")


if __name__ == "__main__":
    ensure_database(force_seed=False)
