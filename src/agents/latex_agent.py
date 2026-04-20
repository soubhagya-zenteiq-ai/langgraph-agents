from typing import Dict, Any
from .base_agent import BaseAgent
from src.utils.prompts import load_prompt
from src.utils.parsers import extract_code_and_lang

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
        # Try to extract from code blocks first
        lang, code = extract_code_and_lang(ai_response)
        if not code:
            code = ai_response # Fallback to raw response if no blocks found

        execution_result = self.latex.compile(code)

        return {
            "final_answer": ai_response,
            "execution_result": execution_result,
            "agent_used": "latex_agent"
        }
