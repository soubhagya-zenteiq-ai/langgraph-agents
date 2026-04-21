"""
Agent designed for web-related queries and information retrieval.
Utilizes web search tools to gather real-time data from the internet.
Processes search results to provide informed answers to user queries.
"""
from typing import Dict, Any

from .base_agent import BaseAgent
from src.utils.prompts import load_prompt
from src.api.schemas.service_responses import AgentResult


class WebAgent(BaseAgent):
    def __init__(self, llm_service, web_service):
        super().__init__(llm_service)
        self.web_service = web_service

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("refined_query", state["user_query"])

        # Step 1: search
        results = self.web_service.search(query)

        # Step 2: summarize
        prompt_template = load_prompt("web_prompt")
        prompt = prompt_template.format(query=query, results=results)
        
        summary = self.llm.invoke(prompt)

        result = AgentResult(
            final_answer=summary,
            agent_used="web_agent",
            execution_result=results
        )
        
        return {
            "final_answer": result.final_answer,
            "agent_used": result.agent_used,
            "execution_result": result.execution_result
        }