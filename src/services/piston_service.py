"""
Interface for the Piston code execution engine.
Handles language runtime detection, installation, and secure code execution.
Enables the system to run arbitrary code in isolated, temporary environments.
"""
import httpx

from typing import Dict, Any, List, Optional

from src.config.settings import settings

from src.api.schemas.service_responses import ExecutionResult

class PistonService:
    def __init__(self, url: Optional[str] = None):
        self.url = url or settings.PISTON_URL

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

    def execute(self, language: str, code: str) -> ExecutionResult:
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
            "files": [{"content": code}]
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(f"{self.url}/api/v2/execute", json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                run = data.get("run", {})
                
                return ExecutionResult(
                    success=run.get("code") == 0,
                    stdout=run.get("stdout", ""),
                    stderr=run.get("stderr", ""),
                    exit_code=run.get("code", -1)
                )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=500
            )
