DB_SCHEMA = {
    "customers": ["id", "name", "city", "age"],
    "employees": ["id", "name", "department", "joining_date"],
    "products": ["id", "name", "category", "price"],
    "sales": ["id", "customer_id", "employee_id", "product_id", "quantity", "sale_amount", "sale_date"]
}

class SchemaAgent:
    def __init__(self):
        self.schema = DB_SCHEMA

    def get_full_schema(self):
        return self.schema

    def identify_relevant_tables(self, question: str):
        q = question.lower()
        relevant = {}

        if any(k in q for k in ["customer", "client"]):
            relevant["customers"] = self.schema["customers"]

        if any(k in q for k in ["employee", "staff"]):
            relevant["employees"] = self.schema["employees"]

        if any(k in q for k in ["product", "item"]):
            relevant["products"] = self.schema["products"]

        if any(k in q for k in ["sale", "revenue", "orders"]):
            relevant["sales"] = self.schema["sales"]

        if not relevant:
            return self.schema  

        return relevant
