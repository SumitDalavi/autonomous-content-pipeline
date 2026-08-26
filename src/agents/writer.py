"""Writer agent: drafts a structured article from research data."""
from __future__ import annotations
import os
from dataclasses import dataclass

from src.agents.researcher import ResearchResult

try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    _LLM_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _LLM_AVAILABLE = False


@dataclass
class Draft:
    topic: str
    title: str
    body: str
    word_count: int = 0
    sources: list = None

    def __post_init__(self):
        self.word_count = len(self.body.split())
        if self.sources is None:
            self.sources = []


_DRAFT_PROMPT = """
You are a senior technical writer. Write a well-structured, insightful article based on the research provided.

Topic: {topic}
Key Facts:
{facts}

Requirements:
- Title: compelling, specific (not generic clickbait)
- Introduction: hook + clear thesis
- 3-4 body sections with H2 subheadings
- Concrete examples and code snippets where relevant
- Conclusion with actionable takeaways
- ~800-1200 words
- Markdown format
"""


def run_writer(research: ResearchResult) -> Draft:
    """
    Generate a full article draft from research. Uses OpenAI if configured,
    falls back to a structured template otherwise.
    """
    print(f"[writer] Drafting article on: {research.topic}")
    facts_text = "\n".join(f"- {f}" for f in research.key_facts[:8])

    if _LLM_AVAILABLE:
        prompt = _DRAFT_PROMPT.format(topic=research.topic, facts=facts_text)
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1800,
            temperature=0.7,
        )
        body = response.choices[0].message.content
        lines = body.strip().split("\n")
        title = lines[0].lstrip("# ").strip() if lines else research.topic
    else:
        # Template fallback for offline/test environments
        title = f"The Complete Guide to {research.topic.title()}"
        facts_section = "\n".join(f"- {f}" for f in research.key_facts[:6])
        body = f"""# {title}

## Introduction
{research.summary}

## Key Insights
{facts_section}

## Practical Applications
Understanding {research.topic} enables teams to build more reliable, scalable systems.
By applying the principles covered here, engineers can avoid common pitfalls and
deliver production-quality results faster.

## Best Practices
1. Start with a clear requirements definition
2. Validate assumptions with small proofs of concept
3. Instrument everything for observability from day one
4. Iterate based on real metrics, not intuition

## Conclusion
{research.topic.title()} is a critical skill for modern engineering teams. The
sources and key facts gathered here provide a solid foundation for deeper exploration.

---
*Sources: {', '.join(s['url'] for s in research.sources[:3])}*
"""

    draft = Draft(
        topic=research.topic,
        title=title,
        body=body,
        sources=research.sources,
    )
    print(f"[writer] Draft complete: {draft.word_count} words.")
    return draft
