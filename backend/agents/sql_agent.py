import re
from datetime import date


class SQLGeneratorAgent:
    def __init__(self, schema, dialect: str = "sqlite"):
        self.schema = schema
        self.dialect = dialect if dialect in ("sqlite", "postgres") else "sqlite"

    def _param(self) -> str:
        return "%s" if self.dialect == "postgres" else "?"

    def _year_expr(self, column: str) -> str:
        if self.dialect == "postgres":
            return f"DATE_PART('year', {column})"
        return f"cast(strftime('%Y', {column}) as integer)"

    def _total_sales_last_year_sql(self) -> str:
        if self.dialect == "postgres":
            return """
                SELECT SUM(sale_amount) AS total_sales
                FROM sales
                WHERE sale_date BETWEEN
                DATE_TRUNC('year', CURRENT_DATE - INTERVAL '1 year') AND
                DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1 day';
            """
        return """
            SELECT SUM(sale_amount) AS total_sales
            FROM sales
            WHERE sale_date >= date('now', 'start of year', '-1 year')
              AND sale_date < date('now', 'start of year');
        """

    def _sales_last_year_sql(self) -> str:
        if self.dialect == "postgres":
            return f"""
                SELECT *
                FROM sales
                WHERE {self._year_expr('sale_date')} = {self._year_expr('CURRENT_DATE')} - 1;
            """
        return """
            SELECT *
            FROM sales
            WHERE sale_date >= date('now', 'start of year', '-1 year')
              AND sale_date < date('now', 'start of year');
        """

    def _year_int(self) -> int:
        return date.today().year

    def _year_filter_sql(self, year: int) -> str:
        return f"SELECT * FROM sales WHERE {self._year_expr('sale_date')} = {year};"

    def _total_sales_year_sql(self, year: int) -> str:
        if self.dialect == "postgres":
            return f"""
                SELECT SUM(sale_amount) AS total_sales
                FROM sales
                WHERE {self._year_expr('sale_date')} = {year};
            """
        return f"""
            SELECT SUM(sale_amount) AS total_sales
            FROM sales
            WHERE {self._year_expr('sale_date')} = {year};
        """

    def _employee_highest_sales_sql(self, year: int | None = None) -> str:
        year_clause = ""
        if year is not None:
            year_clause = f"WHERE {self._year_expr('s.sale_date')} = {year}"
        return f"""
            SELECT e.id, e.name, e.department,
                   SUM(s.sale_amount) AS total_sales
            FROM employees e
            JOIN sales s ON e.id = s.employee_id
            {year_clause}
            GROUP BY e.id, e.name, e.department
            ORDER BY total_sales DESC
            LIMIT 1;
        """

    def _product_highest_revenue_sql(self, year: int | None = None) -> str:
        year_clause = ""
        if year is not None:
            year_clause = f"WHERE {self._year_expr('s.sale_date')} = {year}"
        return f"""
            SELECT p.id, p.name, p.category,
                   SUM(s.sale_amount) AS total_revenue
            FROM products p
            JOIN sales s ON p.id = s.product_id
            {year_clause}
            GROUP BY p.id, p.name, p.category
            ORDER BY total_revenue DESC
            LIMIT 1;
        """

    def _quarter_filter_sql(self, year: str, quarter: str) -> str:
        if self.dialect == "postgres":
            return f"""
                SELECT *
                FROM sales
                WHERE DATE_PART('year', sale_date) = {year}
                AND DATE_PART('quarter', sale_date) = {quarter};
            """
        return f"""
            SELECT *
            FROM sales
            WHERE cast(strftime('%Y', sale_date) as integer) = {year}
            AND cast((cast(strftime('%m', sale_date) as integer) - 1) / 3 + 1 as integer) = {quarter};
        """

    def generate_sql(self, question: str):
        q = question.lower().strip()
        p = self._param()

        if "list all customers" in q or "show all customers" in q:
            return {"sql": "SELECT * FROM customers;", "params": []}

        if "list all employees" in q or "show all employees" in q:
            return {"sql": "SELECT * FROM employees;", "params": []}

        if "list all products" in q or "show all products" in q:
            return {"sql": "SELECT * FROM products;", "params": []}

        if "customers from" in q:
            city = q.split("from")[-1].strip()
            return {
                "sql": f"SELECT * FROM customers WHERE LOWER(city) = LOWER({p});",
                "params": [city],
            }

        if "products above" in q:
            price = re.findall(r"\d+", q)
            if price:
                return {
                    "sql": f"SELECT * FROM products WHERE price > {p};",
                    "params": [int(price[0])],
                }

        if "employees in" in q:
            department = q.split("in")[-1].strip()
            return {
                "sql": f"SELECT * FROM employees WHERE LOWER(department) = LOWER({p});",
                "params": [department],
            }

        if "total sales" in q and "last year" in q:
            return {"sql": self._total_sales_last_year_sql(), "params": []}

        if "total sales" in q and "this year" in q:
            return {"sql": self._total_sales_year_sql(self._year_int()), "params": []}

        if ("count of sales" in q or "how many sales" in q) and "last year" in q:
            ly = self._year_int() - 1
            return {
                "sql": f"""
                    SELECT COUNT(*) AS total_sales
                    FROM sales
                    WHERE {self._year_expr('sale_date')} = {ly};
                """,
                "params": [],
            }

        if ("count of sales" in q or "how many sales" in q) and "this year" in q:
            yr = self._year_int()
            return {
                "sql": f"""
                    SELECT COUNT(*) AS total_sales
                    FROM sales
                    WHERE {self._year_expr('sale_date')} = {yr};
                """,
                "params": [],
            }

        if "count of sales" in q or "how many sales" in q:
            year = re.findall(r"\d{4}", q)
            if year:
                yr = int(year[0])
                return {
                    "sql": f"""
                        SELECT COUNT(*) AS total_sales
                        FROM sales
                        WHERE {self._year_expr('sale_date')} = {yr};
                    """,
                    "params": [],
                }

        if ("average sale" in q or "avg sale" in q) and "last year" in q:
            ly = self._year_int() - 1
            return {
                "sql": f"""
                    SELECT AVG(sale_amount) AS avg_sale
                    FROM sales
                    WHERE {self._year_expr('sale_date')} = {ly};
                """,
                "params": [],
            }

        if ("average sale" in q or "avg sale" in q) and "this year" in q:
            yr = self._year_int()
            return {
                "sql": f"""
                    SELECT AVG(sale_amount) AS avg_sale
                    FROM sales
                    WHERE {self._year_expr('sale_date')} = {yr};
                """,
                "params": [],
            }

        if "average sale" in q or "avg sale" in q:
            year = re.findall(r"\d{4}", q)
            if year:
                yr = int(year[0])
                return {
                    "sql": f"""
                        SELECT AVG(sale_amount) AS avg_sale
                        FROM sales
                        WHERE {self._year_expr('sale_date')} = {yr};
                    """,
                    "params": [],
                }

        if ("employee with highest sales" in q or "highest sales employee" in q) and "this year" in q:
            return {"sql": self._employee_highest_sales_sql(self._year_int()), "params": []}

        if "employee with highest sales" in q or "highest sales employee" in q:
            return {"sql": self._employee_highest_sales_sql(None), "params": []}

        if "product with highest revenue" in q and "this year" in q:
            return {"sql": self._product_highest_revenue_sql(self._year_int()), "params": []}

        if "product with highest revenue" in q or "highest revenue product" in q:
            return {"sql": self._product_highest_revenue_sql(None), "params": []}

        if "sales with customer names" in q or "show sales with customers" in q:
            return {
                "sql": """
                    SELECT s.id, c.name AS customer_name, s.sale_amount, s.sale_date
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.id;
                """,
                "params": [],
            }

        if "sales last year" in q:
            return {"sql": self._sales_last_year_sql(), "params": []}

        if "sales this year" in q:
            return {"sql": self._year_filter_sql(self._year_int()), "params": []}

        if "sales in" in q:
            year = re.findall(r"\d{4}", q)
            if year:
                return {"sql": self._year_filter_sql(int(year[0])), "params": []}

        if "q1" in q or "q2" in q or "q3" in q or "q4" in q:
            quarter = q[q.index("q") + 1]
            year_match = re.findall(r"\d{4}", q)
            year = year_match[0] if year_match else str(self._year_int())
            return {"sql": self._quarter_filter_sql(year, quarter), "params": []}

        return {
            "sql": None,
            "params": [],
            "error": "Unsupported query type. Please ask about customers, employees, products, or sales.",
        }
