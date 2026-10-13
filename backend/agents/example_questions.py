from datetime import date
from typing import Any, Dict, List


def current_year() -> int:
    return date.today().year


def current_quarter() -> int:
    return (date.today().month - 1) // 3 + 1


def build_example_groups() -> List[Dict[str, Any]]:
    y = current_year()
    ly = y - 1
    q = current_quarter()
    prev_q = q - 1 if q > 1 else 4
    prev_q_year = y if q > 1 else y - 1

    return [
        {
            "title": "Lists",
            "items": [
                "List all customers",
                "List all employees",
                "List all products",
                "Show all customers",
            ],
        },
        {
            "title": "Customer filters",
            "items": [
                "Customers from Mumbai",
                "Customers from Delhi",
                "Customers from Bangalore",
                "Customers from Chennai",
            ],
        },
        {
            "title": "Product & employee filters",
            "items": [
                "Products above 50000",
                "Products above 100000",
                "Employees in Sales department",
                "Employees in Tech department",
                "Employees in Support department",
            ],
        },
        {
            "title": f"This year ({y})",
            "items": [
                "What is the total sales this year?",
                f"Count of sales in {y}",
                f"How many sales in {y}",
                f"Average sale amount in {y}",
                f"Sales in Q{q} {y}",
                "Sales this year",
                "Employee with highest sales this year",
                "Product with highest revenue this year",
            ],
        },
        {
            "title": f"Last year ({ly})",
            "items": [
                "What is the total sales last year?",
                "Sales last year",
                f"Count of sales in {ly}",
                f"Average sale amount in {ly}",
                f"Sales in Q{prev_q} {prev_q_year}",
            ],
        },
        {
            "title": "Rankings & joins",
            "items": [
                "Employee with highest sales",
                "Product with highest revenue",
                "Sales with customer names",
                "Show sales with customers",
            ],
        },
        {
            "title": "Help",
            "items": ["tell me about this app"],
        },
    ]


def flat_examples() -> List[str]:
    seen = set()
    out: List[str] = []
    for group in build_example_groups():
        for item in group["items"]:
            if item not in seen:
                seen.add(item)
                out.append(item)
    return out
