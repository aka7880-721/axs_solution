from typing import Any, Dict, List, Optional

from db.database import execute_query


class RetrieverAgent:
    def __init__(self, db_config=None):
        self.db = db_config

    def execute_query(self, sql: Optional[str], params=None) -> Dict[str, Any]:
        if not sql:
            return {"error": "No SQL query to execute."}

        rows, err = execute_query(sql, params or [])
        if err:
            return {"error": err}
        return {"rows": rows or []}
