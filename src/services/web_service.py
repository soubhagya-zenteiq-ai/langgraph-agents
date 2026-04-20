import wikipedia
from googlesearch import search as gsearch

class WebService:
    def search(self, query: str):
        results = []
        
        # Try Wikipedia first
        try:
            wiki_summary = wikipedia.summary(query, sentences=3)
            results.append({
                "title": "Wikipedia Summary", 
                "snippet": wiki_summary, 
                "source": "wikipedia"
            })
        except Exception:
            # Handle disambiguation or not found gracefully
            pass

        # Then try Google Search
        try:
            # googlesearch-python returns a generator of URLs
            for url in gsearch(query, num_results=5):
                results.append({
                    "title": url, 
                    "snippet": "Search result link", 
                    "source": "google",
                    "link": url
                })
        except Exception:
            pass

        return results