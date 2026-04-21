"""
Analyzes LLM output to determine the user's intent.
Routes the flow to the appropriate agent (code, web, db, latex) based on detected tasks.
Ensures that specialized queries are handled by the correct downstream nodes.
"""
from typing import Dict, Any

from src.utils.prompts import load_prompt


def router_node(state: Dict[str, Any], llm) -> Dict[str, Any]:
    query = state.get("refined_query", state["user_query"])
    print(f"[THINKING] Classifying intent for: '{query}'")

    prompt_template = load_prompt("router_prompt")
    prompt = prompt_template.format(query=query)

    intent = llm.invoke(prompt).strip().lower()
    print(f"[THINKING] Selected Agent: {intent}")

    return {
        "intent": intent
    }