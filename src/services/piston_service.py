import requests
from typing import Dict, Any

class PistonService:
    def __init__(self, url: str = "http://piston_engine:2000"):
        self.url = url

    def execute(self, language: str, code: str) -> Dict[str, Any]:
        """
        Executes code in the Piston sandbox.
        """
        payload = {
            "language": language,
            "version": "*",
            "files": [
                {
                    "content": code
                }
            ]
        }
        
        try:
            response = requests.post(f"{self.url}/api/v2/execute", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
