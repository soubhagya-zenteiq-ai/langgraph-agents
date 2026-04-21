"""
Manages database-related tasks, including SQL generation and execution.
Converts natural language queries into executable SQL for PostgreSQL.
Processes database results and provides clear explanations to the user.
"""
from typing import Dict, Any

from .base_agent import BaseAgent
from src.utils.prompts import load_prompt
from src.utils.parsers import clean_sql
from src.api.schemas.service_responses import AgentResult


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

        res = AgentResult(
            final_answer=explanation,
            execution_result=result,
            agent_used="db_agent",
            metadata={"sql": cleaned_sql}
        )
        
        return {
            "final_answer": res.final_answer,
            "execution_result": res.execution_result,
            "agent_used": res.agent_used,
            "sql": cleaned_sql,
            "data": res.execution_result 
        }