from typing import Dict, Any
from langchain.tools import tool


class CodeGenerator:
    """
    Core code generation logic (used by both agent and tool)
    """

    def __init__(self, llm_service, prompt_loader):
        self.llm = llm_service
        self.load_prompt = prompt_loader

    def generate(self, query: str) -> Dict[str, Any]:
        prompt_template = self.load_prompt("code_prompt")

        prompt = prompt_template.format(query=query)

        response = self.llm.invoke(prompt)

        return {
            "code": response,
            "status": "success"
        }


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
        return result["code"]

    return generate_code