from langgraph.graph import StateGraph, START, END

from src.graph.state import AgentState

# nodes
from src.graph.nodes.router import router_node
from src.graph.nodes.llm import llm_node
from src.graph.nodes.final import final_node
from src.graph.nodes.cleanup import cleanup_node

# routing
from src.graph.edges.routing import route_by_intent


def build_graph(llm, agents):
    """
    agents = {
        "code": CodeAgent,
        "web": WebAgent,
        "db": DBAgent
    }
    """

    builder = StateGraph(AgentState)

    # -------------------
    # Node wrappers
    # -------------------

    builder.add_node("router", lambda s: router_node(s, llm))
    builder.add_node("llm", lambda s: llm_node(s, llm))

    builder.add_node("code", lambda s: agents["code"].run(s))
    builder.add_node("web", lambda s: agents["web"].run(s))
    builder.add_node("db", lambda s: agents["db"].run(s))

    builder.add_node("final", final_node)
    builder.add_node("cleanup", cleanup_node)

    # -------------------
    # Edges
    # -------------------

    builder.add_edge(START, "llm")
    builder.add_edge("llm", "router")

    builder.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "code": "code",
            "web": "web",
            "db": "db",
        },
    )

    # after agent → final
    builder.add_edge("code", "final")
    builder.add_edge("web", "final")
    builder.add_edge("db", "final")

    builder.add_edge("final", "cleanup")
    builder.add_edge("cleanup", END)

    return builder.compile()