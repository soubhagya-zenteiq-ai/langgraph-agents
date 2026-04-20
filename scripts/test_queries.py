import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.llm_service import LLMService
from src.services.web_service import WebService
from src.services.db_service import DBService
from src.services.piston_service import PistonService

from src.agents.code_agent import CodeAgent
from src.agents.web_agent import WebAgent
from src.agents.db_agent import DBAgent

from src.graph.builder import build_graph


def create_system():
    llm = LLMService()
    web_service = WebService()
    piston_service = PistonService()
    # Using the demo postgres container DSN since we execute this script inside docker exec
    db_service = DBService(dsn="postgresql://user:password@demo_postgres:5432/demo_db")

    agents = {
        "code": CodeAgent(llm, piston_service),
        "web": WebAgent(llm, web_service),
        "db": DBAgent(llm, db_service),
    }

    return build_graph(llm, agents)


def run_tests():
    graph = create_system()

    queries = [
        "List total amount spent by Alice Johnson on all her orders"
    ]

    for q in queries:
        print(f"\n===== QUERY: {q} =====")

        try:
            result = graph.invoke({
                "user_query": q,
                "messages": []
            })
            print("Response:")
            print(result.get("response"))
        except Exception as e:
            print(f"Error executing query: {e}")


if __name__ == "__main__":
    run_tests()