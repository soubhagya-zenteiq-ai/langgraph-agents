"""
Performs post-processing tasks after the workflow is complete.
Manages state cleanup and final logging before returning the result to the API.
Ensures the system is in a clean state for the next request.
"""
from typing import Dict, Any



def cleanup_node(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])

    # prevent token explosion
    return {
        "messages": messages[-8:]
    }