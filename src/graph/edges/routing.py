"""
Contains logic for conditional routing based on user intent.
Maps specific intents (code, web, db, latex) to their corresponding agent nodes.
Allows the graph to dynamically branch based on the type of task detected.
"""
from typing import Literal

from src.graph.state import AgentState


def route_by_intent(state: AgentState) -> Literal["code", "web", "db", "latex"]:
    intent = state.get("intent", "").lower().strip()

    if intent == "code":
        return "code"

    elif intent == "web":
        return "web"

    elif intent == "db":
        return "db"
        
    elif intent == "latex":
        return "latex"

    # fallback
    return "web"