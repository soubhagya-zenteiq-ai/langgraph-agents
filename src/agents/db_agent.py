from typing import Dict, Any
from .base_agent import BaseAgent
from src.utils.prompts import load_prompt
from src.utils.parsers import clean_sql


class DBAgent(BaseAgent):
    def __init__(self, llm_service, db_service):
        super().__init__(llm_service)
        self.db = db_service

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("refined_query", state["user_query"])

        # Step 1: convert natural language → SQL
        prompt_template = load_prompt("db_prompt")
        prompt = prompt_template.format(query=query)
        
        sql_query = self.llm.invoke(prompt)
        cleaned_sql = clean_sql(sql_query.strip())

        # Step 2: execute
        result = self.db.execute(cleaned_sql)

        # Step 3: explain result
        explanation = self.llm.invoke(f"""
        The user asked: {query}
        The SQL query executed was: {cleaned_sql}
        The database returned: {result}
        
        Provide a concise natural language explanation of this result.
        """)

        return {
            "final_answer": explanation,
            "data": result,
            "sql": cleaned_sql,
            "agent_used": "db_agent"
        }