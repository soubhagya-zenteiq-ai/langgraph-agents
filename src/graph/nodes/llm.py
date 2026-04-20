from typing import Dict, Any


def llm_node(state: Dict[str, Any], llm) -> Dict[str, Any]:
    # If we are in a retry/refinement loop, use the refined_query which contains errors
    # unless it's the first time
    if state.get("retry_count", 0) > 0 and "previous attempt failed" in state.get("refined_query", ""):
        print(f"[THINKING] Retrying with error feedback...")
        return {} # Keep existing refined_query

    query = state["user_query"]
    print(f"\n[THINKING] Refining query: '{query}'")

    refined = llm.invoke(f"""
    Rewrite the following user query to be more precise for a search engine or database.
    Return ONLY the refined query string. No explanations, no lists.
    
    Original Query: {query}
    """)

    print(f"[THINKING] Refined to: '{refined}'")

    return {
        "refined_query": refined
    }