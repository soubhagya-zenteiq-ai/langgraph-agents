"""
Implementation of the web search tool.
Interfaces with Wikipedia and Google Search to retrieve relevant snippets and URLs.
Provides a unified interface for gathering real-time data from multiple web sources.
"""
from typing import List, Optional
from langchain.tools import tool
import wikipedia
from googlesearch import search as gsearch
from src.api.schemas.service_responses import WebSearchResponse, SearchResult

class WebSearchTool:
    """
    Performs web search using Wikipedia and Google Search.
    """

    def search(self, query: str) -> WebSearchResponse:
        results = []
        
        # Try Wikipedia first
        try:
            wiki_summary = wikipedia.summary(query, sentences=3)
            results.append(SearchResult(
                title="Wikipedia Summary", 
                snippet=wiki_summary, 
                source="wikipedia"
            ))
        except Exception:
            pass

        # Then try Google Search
        try:
            for url in gsearch(query, num_results=5):
                results.append(SearchResult(
                    title=url, 
                    snippet="External Link", 
                    source="google", 
                    link=url
                ))
        except Exception:
            pass

        return WebSearchResponse(
            status="success" if results else "empty",
            query=query,
            results=results[:5]
        )


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
        return str(result.model_dump())

    return web_search