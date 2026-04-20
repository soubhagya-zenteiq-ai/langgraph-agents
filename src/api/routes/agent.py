from fastapi import APIRouter, HTTPException
from src.graph.builder import build_graph

# services
from src.services.llm_service import LLMService
from src.services.web_service import WebService
from src.services.db_service import DBService
from src.services.piston_service import PistonService
from src.services.latex_service import LatexService

# agents
from src.agents.code_agent import CodeAgent
from src.agents.web_agent import WebAgent
from src.agents.db_agent import DBAgent
from src.agents.latex_agent import LatexAgent

# schema
from src.api.schemas.request import AgentRequest

router = APIRouter()

# -----------------------------
# System bootstrap (singleton style)
# -----------------------------
def create_system():
    llm = LLMService()
    web_service = WebService()
    piston_service = PistonService()
    latex_service = LatexService()
    # Updated DSN for the demo postgres container
    db_service = DBService(dsn="postgresql://user:password@demo_postgres:5432/demo_db")

    agents = {
        "code": CodeAgent(llm, piston_service),
        "web": WebAgent(llm, web_service),
        "db": DBAgent(llm, db_service),
        "latex": LatexAgent(llm, latex_service),
    }

    graph = build_graph(llm, agents)
    return graph

# Create once
graph = create_system()

# -----------------------------
# Endpoint
# -----------------------------
@router.post("/run")
def run_agent(request: AgentRequest):
    try:
        result = graph.invoke({
            "user_query": request.query,
            "messages": []
        })

        return {
            "query": request.query,
            "response": result.get("response")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))