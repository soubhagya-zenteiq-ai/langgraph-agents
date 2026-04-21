"""
Pydantic models for structured service and agent responses.
Ensures consistency in data exchange between services, agents, and the graph.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union


# --- Tool & Service Level Models ---

class SearchResult(BaseModel):
    title: str
    snippet: str
    source: str
    link: Optional[str] = None


class WebSearchResponse(BaseModel):
    status: str
    query: str
    results: List[SearchResult]


class ExecutionResult(BaseModel):
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_s: Optional[float] = None


class DBResponse(BaseModel):
    status: str
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class CodeGeneratorResponse(BaseModel):
    status: str
    code: str


# --- Agent Level Models ---

class AgentResult(BaseModel):
    """
    Standardized result returned by all specialized agents back to the graph.
    """
    final_answer: str
    agent_used: str
    execution_result: Optional[Union[ExecutionResult, DBResponse, WebSearchResponse]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
