from typing import Literal
from src.graph.state import AgentState


def route_by_intent(state: AgentState) -> Literal["code", "web", "db"]:
    intent = state.get("intent", "")

    if intent == "code":
        return "code"

    elif intent == "web":
        return "web"

    elif intent == "db":
        return "db"

    # fallback
    return "web"