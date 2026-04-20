from typing import Dict, Any

def refine_node(state: Dict[str, Any]) -> Dict[str, Any]:
    execution_result = state.get("execution_result", {})
    agent_used = state.get("agent_used", "unknown")
    retry_count = state.get("retry_count", 0)
    
    error_msg = ""
    if agent_used == "latex_agent":
        error_msg = execution_result.get("stderr") or execution_result.get("error") or "Unknown LaTeX error (possibly missing images or packages)."
    elif agent_used == "code_agent":
        error_msg = execution_result.get("run", {}).get("stderr") or execution_result.get("error") or "Unknown Code execution error."

    print(f"[RETRY] Agent {agent_used} failed. Retry count: {retry_count + 1}. Error: {error_msg[:100]}...")

    # Update the query with error information for the next attempt
    current_query = state.get("refined_query", state["user_query"])
    refinement_prompt = f"The previous attempt failed with the following error:\n{error_msg}\n\nPlease fix the issue and provide a corrected version of the code. Query: {current_query}"

    return {
        "refined_query": refinement_prompt,
        "retry_count": retry_count + 1,
        "intermediate_steps": state.get("intermediate_steps", []) + [f"Retry {retry_count + 1}: {error_msg[:50]}"]
    }
