"""Critic agent: scores a draft and returns structured feedback."""
from __future__ import annotations
import os
import re
from dataclasses import dataclass, field
from typing import List

from src.agents.writer import Draft

try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    _LLM_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _LLM_AVAILABLE = False


@dataclass
class CritiqueResult:
    score: float          # 0.0 – 1.0
    passes: bool          # score >= threshold
    feedback: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


_CRITIQUE_PROMPT = """
You are a demanding senior editor. Evaluate this article draft on a scale of 0.0 to 1.0.

Article:
---
{body}
---

Evaluate on:
1. Accuracy and depth of content (0-25pts)
2. Structure and readability (0-25pts)
3. Practical value for the reader (0-25pts)
4. Writing quality and tone (0-25pts)

Respond ONLY in this JSON format:
{{
  "score": 0.00,
  "strengths": ["strength 1", "strength 2"],
  "feedback": ["improvement 1", "improvement 2"]
}}
"""


def run_critic(draft: Draft, threshold: float = 0.80) -> CritiqueResult:
    """
    Evaluate draft quality. Returns a CritiqueResult with a numeric score,
    pass/fail flag, and actionable feedback.
    """
    print(f"[critic] Evaluating draft: {draft.title!r}")

    if _LLM_AVAILABLE:
        prompt = _CRITIQUE_PROMPT.format(body=draft.body[:3000])
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.2,
        )
        raw = response.choices[0].message.content
        try:
            import json
            data = json.loads(raw)
            score = float(data.get("score", 0.0))
            feedback = data.get("feedback", [])
            strengths = data.get("strengths", [])
        except Exception:
            # Fall back to heuristic if JSON parse fails
            score, feedback, strengths = _heuristic_score(draft)
    else:
        score, feedback, strengths = _heuristic_score(draft)

    result = CritiqueResult(
        score=score,
        passes=score >= threshold,
        feedback=feedback,
        strengths=strengths,
    )
    status = "PASS" if result.passes else "FAIL"
    print(f"[critic] Score: {score:.2f} [{status}] (threshold={threshold})")
    return result


def _heuristic_score(draft: Draft):
    """Rule-based quality heuristic for offline evaluation."""
    score = 0.0
    feedback = []
    strengths = []

    if draft.word_count >= 600:
        score += 0.25
        strengths.append("Sufficient length")
    else:
        feedback.append(f"Too short: {draft.word_count} words (target 600+)")

    if "##" in draft.body:
        score += 0.25
        strengths.append("Has section structure")
    else:
        feedback.append("Missing section headings (use ## subheadings)")

    if len(draft.sources) >= 2:
        score += 0.25
        strengths.append("Multiple sources cited")
    else:
        feedback.append("Needs more source citations")

    body_lower = draft.body.lower()
    keywords = ["example", "practice", "implement", "result"]
    if any(k in body_lower for k in keywords):
        score += 0.25
        strengths.append("Includes practical examples")
    else:
        feedback.append("Add concrete examples or implementation details")

    return score, feedback, strengths
