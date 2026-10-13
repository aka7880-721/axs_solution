from typing import Any, Dict, List


def _fmt_money(value: Any) -> str:
    try:
        n = float(value)
        return f"{n:,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _format_row_lines(row: Dict[str, Any]) -> str:
    lines = []
    for key, value in row.items():
        label = key.replace("_", " ").strip().title()
        if key in ("total_sales", "total_revenue", "avg_sale", "sale_amount", "price"):
            lines.append(f"{label}: {_fmt_money(value)}")
        else:
            lines.append(f"{label}: {value}")
    return "\n".join(lines)


class SynthesizerAgent:
    def synthesize(self, question, sql, rows):
        q = question.lower()

        if not rows:
            return "No matching results were returned."

        try:
            row = rows[0]

            if ("total" in q or "sum" in q) and "sales" in q:
                return f"The total sales amount is {_fmt_money(row.get('total_sales'))}."

            if "how many" in q or "count" in q:
                count_val = row.get("total_sales") or row.get("count")
                return f"The total count is {count_val}."

            if "average" in q or "avg" in q:
                return f"The average sale amount is {_fmt_money(row.get('avg_sale'))}."

            if "employee" in q and ("highest" in q or "top" in q):
                name = row.get("name", "Unknown")
                dept = row.get("department", "")
                sales = _fmt_money(row.get("total_sales"))
                dept_part = f" ({dept})" if dept else ""
                return f"{name}{dept_part} has the highest sales: {sales}."

            if "product" in q and ("highest" in q or "revenue" in q):
                name = row.get("name", "Unknown")
                rev = _fmt_money(row.get("total_revenue"))
                if "this year" in q:
                    return f"{name} has the highest revenue this year: {rev}."
                return f"{name} has the highest revenue: {rev}."

            if "top" in q or "highest" in q:
                return "Top result:\n" + _format_row_lines(row)

            if "list" in q or "show" in q:
                if len(rows) == 1:
                    return "Found 1 record:\n" + _format_row_lines(row)
                return f"Found {len(rows)} records. First row:\n" + _format_row_lines(row)

            if len(rows) == 1:
                return _format_row_lines(row)

            return f"Found {len(rows)} results. First row:\n" + _format_row_lines(row)

        except Exception as e:
            return f"An error occurred while generating the answer: {e}"
