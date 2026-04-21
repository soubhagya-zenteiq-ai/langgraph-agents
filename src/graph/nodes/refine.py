"""
Handles query refinement and self-correction logic.
If an agent execution fails, this node updates the query with error context.
Ensures that subsequent attempts have better information to resolve issues.
"""
from typing import Dict, Any
from src.api.schemas.service_responses import ExecutionResult


def refine_node(state: Dict[str, Any]) -> Dict[str, Any]:
    execution_result = state.get("execution_result")
    agent_used = state.get("agent_used", "unknown")
    retry_count = state.get("retry_count", 0)
    
    error_msg = ""
    if isinstance(execution_result, ExecutionResult):
        error_msg = execution_result.stderr or execution_result.stdout or "Execution failed without specific logs."
    elif isinstance(execution_result, dict):
        # Fallback for old dict-based data
        error_msg = str(execution_result.get("error", "Unknown error"))
    else:
        error_msg = "Unknown execution failure."

    print(f"[RETRY] Agent {agent_used} failed. Retry count: {retry_count + 1}. Error: {error_msg[:100]}...")

    # Update the query with error information for the next attempt
    current_query = state.get("refined_query", state["user_query"])
    refinement_prompt = f"The previous attempt failed with the following error:\n{error_msg}\n\nPlease fix the issue and provide a corrected version of the code. Original Query: {current_query}"

    return {
        "refined_query": refinement_prompt,
        "retry_count": retry_count + 1,
        "intermediate_steps": state.get("intermediate_steps", []) + [f"Retry {retry_count + 1}: {error_msg[:50]}"]
    }
