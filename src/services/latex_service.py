"""
Provides LaTeX compilation capabilities.
Communicates with a LaTeX server to transform TeX code into rendered outputs.
Manages file paths and ensures that generated documents are correctly stored.
"""
import httpx

from typing import Dict, Any, Optional
from src.config.settings import settings

from src.api.schemas.service_responses import ExecutionResult

class LatexService:
    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.LATEX_URL

    def compile(self, code: str) -> ExecutionResult:
        """
        Compiles LaTeX code using the LaTeX checker service.
        """
        payload = {"code": code}
        
        try:
            with httpx.Client() as client:
                response = client.post(self.url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                return ExecutionResult(
                    success=data.get("exit_code") == 0,
                    stdout=data.get("stdout", ""),
                    stderr=data.get("stderr", ""),
                    exit_code=data.get("exit_code", -1)
                )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=500
            )
