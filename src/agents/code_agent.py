"""
Specialized agent for handling programming and code execution tasks.
Generates code using the LLM and executes it securely in a Piston sandbox.
Returns both the AI's explanation and the raw execution output.
"""
from typing import Dict, Any

from .base_agent import BaseAgent
from src.utils.prompts import load_prompt
from src.utils.parsers import extract_code_and_lang
from src.api.schemas.service_responses import AgentResult


class CodeAgent(BaseAgent):
    def __init__(self, llm_service, piston_service):
        super().__init__(llm_service)
        self.piston = piston_service

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("refined_query", state["user_query"])

        prompt_template = load_prompt("code_prompt")
        prompt = prompt_template.format(query=query)

        ai_response = self.llm.invoke(prompt)

        # Sandbox execution
        lang, code = extract_code_and_lang(ai_response)
        print(f"[THINKING] Identified language: {lang}")
        execution_result = self.piston.execute(lang, code)

        result = AgentResult(
            final_answer=ai_response,
            execution_result=execution_result,
            agent_used="code_agent",
            metadata={"language": lang}
        )
        
        # Return as dict for LangGraph state update
        return {
            "final_answer": result.final_answer,
            "execution_result": result.execution_result,
            "agent_used": result.agent_used,
            "metadata": result.metadata
        }