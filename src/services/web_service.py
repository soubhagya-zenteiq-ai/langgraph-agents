"""
Core service for web interactions and search tasks.
Wraps Wikipedia and Google Search APIs for information retrieval.
Enables the Web Agent to gather and process real-time data from the internet.
"""
import wikipedia
from googlesearch import search as gsearch
from src.api.schemas.service_responses import WebSearchResponse, SearchResult

class WebService:
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
            # googlesearch-python returns a generator of URLs
            for url in gsearch(query, num_results=5):
                results.append(SearchResult(
                    title=url, 
                    snippet="Search result link", 
                    source="google",
                    link=url
                ))
        except Exception:
            pass

        return WebSearchResponse(
            status="success" if results else "empty",
            query=query,
            results=results
        )