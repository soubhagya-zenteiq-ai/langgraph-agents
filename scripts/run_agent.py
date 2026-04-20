import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.llm_service import LLMService
from src.services.web_service import WebService
from src.services.db_service import DBService
from src.services.piston_service import PistonService
from src.services.latex_service import LatexService

from src.agents.code_agent import CodeAgent
from src.agents.web_agent import WebAgent
from src.agents.db_agent import DBAgent
from src.agents.latex_agent import LatexAgent

from src.graph.builder import build_graph

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py 'your query'")
        sys.exit(1)

    query = sys.argv[1]

    llm = LLMService()
    web_service = WebService()
    piston_service = PistonService()
    latex_service = LatexService()
    db_service = DBService(dsn="postgresql://user:password@demo_postgres:5432/demo_db")

    agents = {
        "code": CodeAgent(llm, piston_service),
        "web": WebAgent(llm, web_service),
        "db": DBAgent(llm, db_service),
        "latex": LatexAgent(llm, latex_service),
    }

    graph = build_graph(llm, agents)
    
    print(f"Running query: {query}")
    result = graph.invoke({
        "user_query": query,
        "messages": []
    })

    print("-" * 30)
    print("FINAL RESPONSE:")
    print(result.get("response"))
    print("-" * 30)

if __name__ == "__main__":
    main()
