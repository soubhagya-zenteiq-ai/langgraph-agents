from typing import Dict, Any
from .base_agent import BaseAgent
from src.utils.prompts import load_prompt


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

        return {
            "final_answer": summary,
            "agent_used": "web_agent",
            "tool_output": results
        }