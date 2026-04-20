from typing import Dict, Any


def tool_executor_node(state: Dict[str, Any], tools_by_name) -> Dict[str, Any]:
    last_message = state["messages"][-1]

    outputs = []

    if hasattr(last_message, "tool_calls"):
        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            result = tool.invoke(tool_call["args"])

            outputs.append({
                "tool": tool_call["name"],
                "result": result
            })

    return {
        "tool_output": outputs
    }