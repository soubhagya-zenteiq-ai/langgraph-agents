import httpx
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SandboxManager:
    # Local URL of your Piston service
    PISTON_URL = "http://piston-engine:2000/api/v2/execute"
    
    # Supported languages that Piston handles (+ latex routed separately)
    SUPPORTED_LANGUAGES = {"python", "javascript", "go", "cpp", "java", "ruby", "latex"}

    @staticmethod
    def detect_language(code: str) -> str:
        """Simple language detection based on syntax patterns"""
        import re
        patterns = {
            # LaTeX MUST be checked first
            'latex': [
                r'\\documentclass',
                r'\\begin\{document\}',
                r'\\usepackage',
                r'\\section\{',
            ],
            'python': [r'def\s+\w+\s*\(', r'import\s+\w+', r'print\s*\(', r'while\s+', r'for\s+\w+\s+in'],
            'javascript': [r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'console\.log', r'let\s+\w+\s*='],
            'java': [r'public\s+class', r'public\s+static\s+void\s+main'],
            'cpp': [r'#include\s*<', r'int\s+main\s*\(', r'std::'],
            'go': [r'package\s+main', r'func\s+main\s*\('],
            'ruby': [r'def\s+\w+', r'puts\s+', r'class\s+\w+'],
        }

        for lang, lang_patterns in patterns.items():
            if any(re.search(pattern, code, re.IGNORECASE) for pattern in lang_patterns):
                return lang

        return 'python'  # Default

    @staticmethod
    async def run_latex(code: str) -> Dict[str, Any]:
        """
        Compiles LaTeX code by sending it to the latex_checker internal HTTP server.
        Returns success/failure with compiler output.
        """
        t_start = time.perf_counter()
        logger.info("--- LATEX PHASE: Starting LaTeX compilation check ---")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post("http://latex-checker:3000/", json={"code": code})
                data = response.json()
                
            exit_code = data.get("exit_code", -1)
            stdout = data.get("stdout", "") or ""
            stderr = data.get("stderr", "") or ""
            
            duration = time.perf_counter() - t_start
            success = exit_code == 0

            # Extract just the error lines to keep the output clean
            error_lines = [
                line for line in stdout.splitlines()
                if line.startswith("!") or "Error" in line or "error" in line
            ]
            clean_stderr = "\n".join(error_lines) if error_lines else stderr

            logger.info(f"--- LATEX PHASE: COMPLETE (Success: {success}) (Time: {duration:.3f}s) ---")

            return {
                "success": success,
                "stdout": str(stdout)[:2000],
                "stderr": str(clean_stderr)[:500],
                "exit_code": exit_code,
                "duration_s": duration
            }

        except httpx.ReadTimeout:
            return {
                "success": False,
                "stdout": "",
                "stderr": "LaTeX compilation timed out after 30 seconds.",
                "exit_code": 124,
                "duration_s": 30.0
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"LaTeX execution error: {e}",
                "exit_code": 500,
                "duration_s": time.perf_counter() - t_start
            }

    @staticmethod
    async def run_code(code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes code using the locally running Piston engine.
        Routes LaTeX to the dedicated latex_checker container.
        """
        lang_detected = SandboxManager.detect_language(code)
        
        if language and language.lower().strip() != lang_detected:
            logger.info(f"AI suggested '{language}', but regex detected '{lang_detected}'. Overriding to '{lang_detected}'.")
            
        lang_clean = lang_detected

        # 1. Route LaTeX separately
        if lang_clean == "latex":
            return await SandboxManager.run_latex(code)

        # 2. Validation Layer
        if lang_clean not in SandboxManager.SUPPORTED_LANGUAGES:
            error_msg = f"Unsupported language '{lang_clean}'. Supported: {', '.join(SandboxManager.SUPPORTED_LANGUAGES)}"
            logger.warning(error_msg)
            return {"success": False, "stdout": "", "stderr": error_msg, "exit_code": -1}

        logger.info(f"--- SANDBOX PHASE: STARTing Piston execution for '{lang_clean}' ---")
        
        lang_map = {
            "python": "python", 
            "javascript": "javascript", 
            "go": "go", 
            "cpp": "cpp", 
            "java": "java", 
            "ruby": "ruby"
        }
        piston_lang = lang_map.get(lang_clean, lang_clean)

        payload = {
            "language": piston_lang,
            "version": "*",
            "files": [{"content": code}]
        }

        try:
            t_sandbox_start = time.perf_counter()
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(SandboxManager.PISTON_URL, json=payload)
                data = response.json()
                
                run = data.get("run")
                if not run:
                    error_msg = data.get("message", "Unknown Piston Error")
                    logger.warning(f"   [Sandbox] Piston Error: {error_msg}")
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": error_msg,
                        "exit_code": -1,
                        "duration_s": time.perf_counter() - t_sandbox_start
                    }
                
                t_sandbox_end = time.perf_counter()
                
                output: Dict[str, Any] = {
                    "success": run.get("code") == 0,
                    "stdout": run.get("stdout", ""),
                    "stderr": run.get("stderr", ""),
                    "exit_code": run.get("code", -1),
                    "duration_s": t_sandbox_end - t_sandbox_start
                }
                
                logger.info(f"--- SANDBOX PHASE: COMPLETE (Exit Code: {output['exit_code']}) (Time: {output['duration_s']}s) ---")
                
                stderr_text = output.get("stderr", "")
                if isinstance(stderr_text, str) and stderr_text:
                    truncated_stderr = stderr_text[:100]
                    logger.warning(f"   [Sandbox] Error detected in stderr: {truncated_stderr}...")
                
                return output
                
        except httpx.ReadTimeout:
            timeout_msg = "Piston execution timed out. Code might be in an infinite loop."
            logger.error(timeout_msg)
            return {"success": False, "stderr": timeout_msg, "exit_code": 124, "duration_s": 20.0}
        except Exception as e:
            crash_msg = f"Piston execution failed: {e}"
            logger.error(crash_msg)
            return {"success": False, "stderr": crash_msg, "exit_code": 500}