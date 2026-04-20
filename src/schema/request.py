from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    prompt: str = Field(..., description="The coding task or query from the user.")

class SandboxOutput(BaseModel):
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: int
    success: bool

class DetailedAgentResponse(BaseModel):
    status: str
    query: str
    ai_response_code: Optional[str] = None
    code_language: Optional[str] = None
    sandbox_output: Optional[SandboxOutput] = None
    is_compilable: bool
    final_answer: str
    execution_time: Optional[Dict[str, float]] = None