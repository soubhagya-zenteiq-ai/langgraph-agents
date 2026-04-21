"""
Defines the shared state for the LangGraph workflow.
The AgentState tracks queries, intents, tool execution results, and metadata.
Ensures consistency and data flow across all nodes in the agent network.
"""
from typing import TypedDict, Annotated, List, Dict, Any, Union
import operator
from src.api.schemas.service_responses import ExecutionResult, DBResponse, WebSearchResponse


class AgentState(TypedDict, total=False):
    # Core
    user_query: str
    intent: str

    # Conversation - Accumulates messages
    messages: Annotated[List[Any], operator.add]

    # Tool / agent flow
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Any

    # Control
    refined_query: str
    intermediate_steps: List[str]

    # Output
    final_answer: str
    response: str
    
    # Execution Metadata
    execution_result: Union[ExecutionResult, DBResponse, WebSearchResponse, Any]
    agent_used: str
    retry_count: int
    errors: List[str]
    sql: str
    data: Any
    metadata: Dict[str, Any]