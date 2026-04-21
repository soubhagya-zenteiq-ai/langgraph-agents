"""
Implements retry logic for agent executions.
Checks for errors in the execution results of specialized agents (like Code or LaTeX).
Decides whether to trigger a refinement step or proceed to the final answer.
"""
from typing import Literal, Dict, Any
from src.api.schemas.service_responses import ExecutionResult


def should_retry(state: Dict[str, Any]) -> Literal["retry", "continue"]:
    execution_result = state.get("execution_result")
    retry_count = state.get("retry_count", 0)
    agent_used = state.get("agent_used")

    # Only retry if there's an error and we haven't hit the limit
    if not execution_result or not isinstance(execution_result, ExecutionResult):
        return "continue"

    # Check for errors in execution result
    has_error = not execution_result.success or bool(execution_result.stderr)

    if has_error and retry_count < 2:
        print(f"[RETRY] Error detected in {agent_used}. Triggering refine (Attempt {retry_count + 1})")
        return "retry"

    return "continue"
