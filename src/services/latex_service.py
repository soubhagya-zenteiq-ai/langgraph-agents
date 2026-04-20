import httpx
from typing import Dict, Any

class LatexService:
    def __init__(self, url: str = "http://latex-checker:3000"):
        self.url = url

    def compile(self, code: str) -> Dict[str, Any]:
        """
        Compiles LaTeX code using the LaTeX checker service.
        """
        payload = {"code": code}
        
        try:
            with httpx.Client() as client:
                response = client.post(self.url, json=payload, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}
