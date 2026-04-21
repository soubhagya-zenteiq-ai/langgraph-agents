"""
Utility for generating boilerplate or specific code structures.
Assists the Code Agent in producing valid and runnable source code.
Can be used as a standalone module or wrapped as a LangChain tool.
"""
from typing import Dict, Any
from langchain.tools import tool
from src.api.schemas.service_responses import CodeGeneratorResponse


class CodeGenerator:
    """
    Core code generation logic (used by both agent and tool)
    """

    def __init__(self, llm_service, prompt_loader):
        self.llm = llm_service
        self.load_prompt = prompt_loader

    def generate(self, query: str) -> CodeGeneratorResponse:
        prompt_template = self.load_prompt("code_prompt")
        prompt = prompt_template.format(query=query)
        response = self.llm.invoke(prompt)

        return CodeGeneratorResponse(
            status="success",
            code=response
        )


# -----------------------------
# Optional: LangChain Tool
# -----------------------------

def create_code_tool(code_generator: CodeGenerator):
    """
    Wrap generator as LLM-callable tool
    """

    @tool
    def generate_code(query: str) -> str:
        """
        Generate production-ready code from a natural language query.
        """
        result = code_generator.generate(query)
        return result.code

    return generate_code