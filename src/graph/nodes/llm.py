from typing import Dict, Any


def llm_node(state: Dict[str, Any], llm) -> Dict[str, Any]:
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