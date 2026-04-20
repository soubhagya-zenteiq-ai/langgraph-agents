from typing import TypedDict, Annotated, List, Dict, Any
import operator


class AgentState(TypedDict, total=False):
    # Core
    user_query: str
    intent: str

    # Conversation
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
    execution_result: Any
    agent_used: str
    retry_count: int
    errors: List[str]
    sql: str
    data: Any