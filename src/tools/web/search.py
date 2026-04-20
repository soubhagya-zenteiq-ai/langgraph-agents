from typing import Dict, Any, List
from langchain.tools import tool
import wikipedia
from googlesearch import search as gsearch

class WebSearchTool:
    """
    Performs web search using Wikipedia and Google Search.
    """

    def search(self, query: str) -> Dict[str, Any]:
        results = []
        
        # Try Wikipedia first
        try:
            wiki_summary = wikipedia.summary(query, sentences=3)
            results.append({"title": "Wikipedia Summary", "snippet": wiki_summary, "source": "wikipedia"})
        except Exception:
            pass

        # Then try Google Search
        try:
            for url in gsearch(query, num_results=5):
                results.append({"title": url, "snippet": "External Link", "source": "google", "link": url})
        except Exception:
            pass

        return {
            "status": "success" if results else "empty",
            "query": query,
            "results": results[:5]
        }


# -----------------------------
# LangChain Tool Wrapper
# -----------------------------

def create_web_search_tool():
    @tool
    def web_search(query: str) -> str:
        """
        Search the web/Wikipedia for relevant information.
        """
        tool = WebSearchTool()
        result = tool.search(query)
        return str(result)

    return web_search