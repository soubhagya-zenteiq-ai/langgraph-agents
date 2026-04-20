from typing import Dict, Any
from langchain.tools import tool


class SQLQueryBuilder:
    """
    Converts natural language into a safe PostgreSQL SELECT query.
    """

    def __init__(self, llm_service, prompt_loader):
        self.llm = llm_service
        self.load_prompt = prompt_loader

    def build(self, query: str, schema_hint: str | None = None) -> Dict[str, Any]:
        prompt_template = self.load_prompt("db_prompt")

        schema_text = schema_hint if schema_hint else "No schema hint provided."

        prompt = (
            prompt_template
            + "\n\nDatabase Schema Hint:\n"
            + schema_text
            + "\n\nUser Query:\n"
            + query
        )

        sql = self.llm.invoke(prompt).strip()

        return {
            "sql_query": sql,
            "status": "success"
        }


def create_sql_query_builder_tool(query_builder: SQLQueryBuilder):
    @tool
    def build_sql_query(query: str) -> str:
        """
        Convert a natural language request into a safe PostgreSQL SELECT query.
        """
        result = query_builder.build(query)
        return result["sql_query"]

    return build_sql_query