from typing import Dict, Any


def cleanup_node(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])

    # prevent token explosion
    return {
        "messages": messages[-8:]
    }