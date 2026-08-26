"""Researcher agent: gathers and synthesises web sources on a topic."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import List

from src.tools.search_tool import web_search, fetch_url


@dataclass
class ResearchResult:
    topic: str
    sources: List[dict] = field(default_factory=list)
    summary: str = ""
    key_facts: List[str] = field(default_factory=list)


def run_researcher(topic: str, depth: int = 3) -> ResearchResult:
    """
    Search multiple angles of a topic, fetch top sources, and return
    a structured ResearchResult with key facts and source URLs.
    """
    print(f"[researcher] Searching for: {topic}")
    result = ResearchResult(topic=topic)

    # Search from multiple angles for richer coverage
    queries = [topic, f"{topic} latest developments", f"{topic} best practices 2026"]
    seen_urls = set()

    for query in queries[:depth]:
        hits = web_search(query, max_results=3)
        for hit in hits:
            if hit["url"] not in seen_urls:
                seen_urls.add(hit["url"])
                result.sources.append(hit)

    # Extract key facts from source snippets
    combined = " ".join(s["content"] for s in result.sources)
    sentences = [s.strip() for s in combined.split(".") if len(s.strip()) > 40]
    result.key_facts = sentences[:10]  # top 10 key facts
    result.summary = f"Research on '{topic}' gathered {len(result.sources)} sources covering recent developments, best practices, and technical details."

    print(f"[researcher] Done. {len(result.sources)} sources, {len(result.key_facts)} key facts.")
    return result
