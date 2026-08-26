"""
Autonomous Content Pipeline
===========================
Self-correcting loop: Research → Write → Critique → [Revise if needed] → Publish.
Only publishes when quality score meets the configured threshold.
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

from src.agents.researcher import run_researcher, ResearchResult
from src.agents.writer import run_writer, Draft
from src.agents.critic import run_critic, CritiqueResult
from src.agents.publisher import run_publisher, PublishResult


@dataclass
class PipelineResult:
    topic: str
    draft: Optional[Draft] = None
    critique: Optional[CritiqueResult] = None
    publish: Optional[PublishResult] = None
    iterations: int = 0
    success: bool = False
    reason: str = ""


def run_pipeline(
    topic: str,
    max_iterations: int = 3,
    quality_threshold: float = None,
    output_dir: str = None,
) -> PipelineResult:
    """
    Execute the full autonomous content pipeline for a given topic.

    Args:
        topic: The subject to research and write about.
        max_iterations: Max write → critique cycles before giving up.
        quality_threshold: Score (0.0-1.0) required to publish. Reads from
                           env QUALITY_THRESHOLD if not specified.
        output_dir: Where to save published articles.

    Returns:
        PipelineResult with the full execution history.
    """
    if quality_threshold is None:
        quality_threshold = float(os.getenv("QUALITY_THRESHOLD", "0.80"))
    if output_dir is None:
        output_dir = os.getenv("OUTPUT_DIR", "output")

    result = PipelineResult(topic=topic)

    print(f"\n{'='*60}")
    print(f"Pipeline starting for topic: {topic!r}")
    print(f"Quality threshold: {quality_threshold:.0%} | Max iterations: {max_iterations}")
    print(f"{'='*60}\n")

    # ── Step 1: Research ──────────────────────────────────────────────────────
    research: ResearchResult = run_researcher(topic)

    # ── Step 2–3: Write → Critique loop ──────────────────────────────────────
    draft: Optional[Draft] = None
    critique: Optional[CritiqueResult] = None

    for i in range(1, max_iterations + 1):
        result.iterations = i
        print(f"\n[pipeline] Iteration {i}/{max_iterations}")

        draft = run_writer(research)
        result.draft = draft

        critique = run_critic(draft, threshold=quality_threshold)
        result.critique = critique

        if critique.passes:
            print(f"[pipeline] Quality gate PASSED on iteration {i} (score={critique.score:.2f})")
            break

        print(f"[pipeline] Quality gate FAILED (score={critique.score:.2f}). Revising...")
        # Inject critic feedback into the research summary so the next
        # write iteration addresses the specific gaps.
        feedback_text = "; ".join(critique.feedback)
        research.summary += f" [REVISION NOTES: {feedback_text}]"

    # ── Step 4: Publish if quality gate passed ────────────────────────────────
    if critique and critique.passes and draft:
        publish = run_publisher(draft, output_dir)
        result.publish = publish
        result.success = True
        result.reason = f"Published after {result.iterations} iteration(s)"
    else:
        result.success = False
        result.reason = (
            f"Quality threshold ({quality_threshold:.0%}) not met after "
            f"{max_iterations} iterations (final score: {critique.score:.2f})"
            if critique else "No critique produced"
        )
        print(f"[pipeline] ABORTED: {result.reason}")

    print(f"\n{'='*60}")
    print(f"Pipeline finished | Success: {result.success}")
    print(f"Reason: {result.reason}")
    print(f"{'='*60}\n")
    return result
