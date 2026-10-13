import random
from datetime import date, timedelta

from faker import Faker

from db.database import connect_postgres, connect_sqlite, get_db_config

fake = Faker()

SEED_VERSION = 3


def _placeholder(backend: str) -> str:
    return "%s" if backend == "postgres" else "?"


def _random_sale_date(today: date) -> date:
    """Bias toward the current calendar year so demos feel up to date."""
    roll = random.random()
    y = today.year
    if roll < 0.55:
        start = date(y, 1, 1)
        end = today
    elif roll < 0.8:
        start = date(y - 1, 1, 1)
        end = date(y - 1, 12, 31)
    else:
        start = date(y - 3, 1, 1)
        end = date(y - 2, 12, 31)
    span = (end - start).days
    return start + timedelta(days=random.randint(0, max(span, 0)))


def set_seed_version(version: int) -> None:
    cfg = get_db_config()
    if cfg["backend"] != "sqlite":
        return
    conn = connect_sqlite(cfg["path"])
    conn.execute(f"PRAGMA user_version = {int(version)}")
    conn.commit()
    conn.close()


def get_seed_version() -> int:
    cfg = get_db_config()
    if cfg["backend"] != "sqlite":
        return SEED_VERSION
    path = cfg["path"]
    from pathlib import Path

    if not Path(path).exists():
        return 0
    conn = connect_sqlite(path)
    cur = conn.cursor()
    cur.execute("PRAGMA user_version")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return int(row[0]) if row else 0


def seed() -> None:
    cfg = get_db_config()
    backend = cfg["backend"]
    ph = _placeholder(backend)

    if backend == "sqlite":
        conn = connect_sqlite(cfg["path"])
    else:
        conn = connect_postgres(cfg)

    cur = conn.cursor()

    cur.execute("DELETE FROM sales;")
    cur.execute("DELETE FROM products;")
    cur.execute("DELETE FROM employees;")
    cur.execute("DELETE FROM customers;")

    customers = []
    for _ in range(200):
        name = fake.name()
        city = random.choice(["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad"])
        age = random.randint(20, 65)
        customers.append((name, city, age))
    cur.executemany(
        f"INSERT INTO customers (name, city, age) VALUES ({ph}, {ph}, {ph});",
        customers,
    )

    employees = []
    for _ in range(50):
        name = fake.name()
        dept = random.choice(["Sales", "Support", "HR", "Tech"])
        join_date = fake.date_between(start_date="-5y", end_date="today")
        if backend == "sqlite":
            join_date = join_date.isoformat()
        employees.append((name, dept, join_date))
    cur.executemany(
        f"INSERT INTO employees (name, department, joining_date) VALUES ({ph}, {ph}, {ph});",
        employees,
    )

    products = []
    for _ in range(50):
        name = (
            random.choice(["Laptop", "Phone", "Tablet", "Headphones", "Monitor", "Keyboard", "Mouse"])
            + " "
            + fake.color_name()
        )
        category = random.choice(["Electronics", "Accessories"])
        price = round(random.uniform(1000, 100000), 2)
        products.append((name, category, price))
    cur.executemany(
        f"INSERT INTO products (name, category, price) VALUES ({ph}, {ph}, {ph});",
        products,
    )

    cur.execute("SELECT id FROM customers;")
    customer_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id FROM employees;")
    employee_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT id FROM products;")
    product_ids = [row[0] for row in cur.fetchall()]

    sales = []
    today = date.today()
    for _ in range(1000):
        customer_id = random.choice(customer_ids)
        employee_id = random.choice(employee_ids)
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 5)
        base_price = random.uniform(1000, 100000)
        sale_amount = round(base_price * quantity, 2)
        sale_date = _random_sale_date(today)
        if backend == "sqlite":
            sale_date = sale_date.isoformat()
        sales.append((customer_id, employee_id, product_id, quantity, sale_amount, sale_date))

    cur.executemany(
        f"""
        INSERT INTO sales (customer_id, employee_id, product_id, quantity, sale_amount, sale_date)
        VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph});
        """,
        sales,
    )

    conn.commit()
    cur.close()
    conn.close()
    set_seed_version(SEED_VERSION)


if __name__ == "__main__":
    seed()
    print("Seeded data successfully.")
