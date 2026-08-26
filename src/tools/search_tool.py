"""Web search tool powered by Tavily for real-time research."""
import os
from typing import List, Dict

try:
    from tavily import TavilyClient
    _client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))
    _TAVILY_AVAILABLE = True
except Exception:
    _TAVILY_AVAILABLE = False


def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search the web for information on query.
    Returns a list of {title, url, content} dicts.
    Falls back to a mock if Tavily is not configured.
    """
    if _TAVILY_AVAILABLE and os.getenv("TAVILY_API_KEY"):
        results = _client.search(query=query, max_results=max_results)
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", "")}
            for r in results.get("results", [])
        ]
    # Mock fallback for local development without API keys
    return [
        {
            "title": f"Mock result for: {query}",
            "url": f"https://example.com/{query.replace(' ', '-')}",
            "content": (
                f"This is simulated search content for the query '{query}'. "
                "In production, real search results from Tavily are used here. "
                "The content would include relevant facts, statistics, and citations."
            ),
        }
    ]


def fetch_url(url: str) -> str:
    """Fetch and return the text content of a URL."""
    try:
        import httpx
        resp = httpx.get(url, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        # Strip HTML tags naively
        import re
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:5000]  # cap at 5k chars
    except Exception as e:
        return f"[fetch error: {e}]"
