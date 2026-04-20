from typing import Literal, Dict, Any

def should_retry(state: Dict[str, Any]) -> Literal["retry", "continue"]:
    execution_result = state.get("execution_result")
    retry_count = state.get("retry_count", 0)
    agent_used = state.get("agent_used")

    # Only retry if there's an error and we haven't hit the limit
    if not execution_result:
        return "continue"

    # Check for errors in execution result
    has_error = False
    
    if agent_used == "latex_agent":
        if "error" in execution_result or not execution_result.get("pdf_filename"):
            has_error = True
    elif agent_used == "code_agent":
        # Piston error check
        if "error" in execution_result or execution_result.get("run", {}).get("stderr"):
            has_error = True

    if has_error and retry_count < 2:
        return "retry"

    return "continue"
