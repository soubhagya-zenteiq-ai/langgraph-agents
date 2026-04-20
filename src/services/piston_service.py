import httpx
from typing import Dict, Any, List

class PistonService:
    def __init__(self, url: str = "http://piston_engine:2000"):
        self.url = url

    def get_runtimes(self) -> List[Dict[str, Any]]:
        """Get list of installed runtimes."""
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.url}/api/v2/runtimes")
                response.raise_for_status()
                return response.json()
        except:
            return []

    def install_runtime(self, language: str) -> Dict[str, Any]:
        """Attempt to install a language runtime."""
        payload = {"language": language, "version": "*"}
        try:
            with httpx.Client() as client:
                response = client.post(f"{self.url}/api/v2/packages", json=payload, timeout=300.0)
                response.raise_for_status()
                res_data = response.json()
                print(f"[SYSTEM] Piston Install Response: {res_data}")
                return res_data
        except Exception as e:
            return {"error": str(e)}

    def execute(self, language: str, code: str) -> Dict[str, Any]:
        """
        Executes code in the Piston sandbox.
        Automatically tries to install the runtime if it's missing.
        """
        # Case-insensitive language check
        lang_lower = language.lower()
        runtimes = self.get_runtimes()
        is_installed = any(
            r["language"].lower() == lang_lower or 
            lang_lower in [a.lower() for a in r.get("aliases", [])] 
            for r in runtimes
        )
        
        if not is_installed:
            print(f"[SYSTEM] Language '{language}' not found in runtimes. Attempting to install...")
            install_res = self.install_runtime(lang_lower)
            if "error" in install_res:
                print(f"[SYSTEM] Failed to install '{language}': {install_res['error']}")
            else:
                print(f"[SYSTEM] Install request for '{language}' sent: {install_res.get('message', 'Success')}")

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
            with httpx.Client() as client:
                response = client.post(f"{self.url}/api/v2/execute", json=payload, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}
