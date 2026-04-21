"""
Low-level database utility for safely executing PostgreSQL queries.
Handles security checks to ensure only read-only SELECT queries are performed.
Provides a LangChain-compatible tool interface for database interactions.
"""
from typing import Dict, Any

from langchain.tools import tool


READ_ONLY_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
    "comment",
    "copy",
}


class PostgresTool:
    """
    Executes safe read-only PostgreSQL queries using DBService.
    """

    def __init__(self, db_service):
        self.db_service = db_service

    def _is_safe_query(self, sql: str) -> bool:
        normalized = sql.strip().lower()

        if not normalized.startswith("select"):
            return False

        for keyword in READ_ONLY_KEYWORDS:
            if keyword in normalized:
                return False

        if ";" in normalized[:-1]:
            return False

        return True

    def run_query(self, sql: str) -> Dict[str, Any]:
        if not self._is_safe_query(sql):
            return {
                "status": "error",
                "error": "Unsafe SQL detected. Only single read-only SELECT queries are allowed."
            }

        result = self.db_service.execute(sql)

        return {
            "status": "success" if "error" not in result else "error",
            "sql_query": sql,
            "result": result
        }


def create_postgres_query_tool(postgres_tool: PostgresTool):
    @tool
    def execute_postgres_query(sql: str) -> str:
        """
        Execute a safe read-only PostgreSQL SELECT query.
        """
        result = postgres_tool.run_query(sql)
        return str(result)

    return execute_postgres_query