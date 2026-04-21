"""
Handles LaTeX document generation and compilation requests.
Transforms natural language descriptions into properly formatted LaTeX code.
Utilizes the LaTeX service to compile and validate the generated documents.
"""
from typing import Dict, Any

from .base_agent import BaseAgent
from src.utils.prompts import load_prompt
from src.utils.parsers import extract_code_and_lang
from src.api.schemas.service_responses import AgentResult


class LatexAgent(BaseAgent):
    def __init__(self, llm_service, latex_service):
        super().__init__(llm_service)
        self.latex = latex_service

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("refined_query", state["user_query"])

        prompt_template = load_prompt("latex_prompt")
        prompt = prompt_template.format(query=query)

        ai_response = self.llm.invoke(prompt)

        # LaTeX compilation
        _, code = extract_code_and_lang(ai_response)
        execution_result = self.latex.compile(code)

        result = AgentResult(
            final_answer=ai_response,
            execution_result=execution_result,
            agent_used="latex_agent"
        )
        
        return {
            "final_answer": result.final_answer,
            "execution_result": result.execution_result,
            "agent_used": result.agent_used
        }
