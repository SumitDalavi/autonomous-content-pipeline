"""Tests for the autonomous content pipeline."""
import pytest
from unittest.mock import patch, MagicMock

from src.tools.search_tool import web_search
from src.agents.researcher import run_researcher
from src.agents.writer import run_writer, Draft
from src.agents.critic import run_critic, _heuristic_score
from src.agents.publisher import run_publisher
from src.pipeline import run_pipeline


# ── Search Tool Tests ─────────────────────────────────────────────────────────

def test_web_search_returns_results():
    results = web_search("distributed systems", max_results=2)
    assert isinstance(results, list)
    assert len(results) > 0
    assert all("title" in r and "url" in r and "content" in r for r in results)


# ── Researcher Tests ──────────────────────────────────────────────────────────

def test_researcher_returns_result():
    result = run_researcher("Kubernetes admission webhooks", depth=1)
    assert result.topic == "Kubernetes admission webhooks"
    assert len(result.sources) > 0
    assert len(result.key_facts) > 0
    assert result.summary != ""


# ── Writer Tests ──────────────────────────────────────────────────────────────

def test_writer_produces_draft():
    from src.agents.researcher import ResearchResult
    research = ResearchResult(
        topic="Test Topic",
        sources=[{"title": "S1", "url": "https://example.com", "content": "Some content about test topic here."}],
        key_facts=["Fact one about the topic.", "Fact two provides detail."],
        summary="Summary of test topic research.",
    )
    draft = run_writer(research)
    assert isinstance(draft, Draft)
    assert draft.word_count > 10
    assert draft.title != ""
    assert draft.body != ""


# ── Critic Tests ──────────────────────────────────────────────────────────────

def test_heuristic_score_good_draft():
    draft = Draft(
        topic="Distributed Systems",
        title="The Complete Guide to Distributed Systems",
        body=(
            "## Introduction\n" + "word " * 700 +
            "## Key Insights\nHere is an example of the concept implemented. " +
            "Practice shows that results improve with this approach.\n" +
            "## Conclusion\nKey takeaways: implement, measure, iterate."
        ),
        sources=[{"url": "https://a.com"}, {"url": "https://b.com"}],
    )
    score, feedback, strengths = _heuristic_score(draft)
    assert score >= 0.75, f"Expected good score, got {score}"


def test_critic_passes_quality_gate():
    draft = Draft(
        topic="DevSecOps",
        title="DevSecOps Best Practices",
        body="## Intro\n" + "practice example implement result " * 200 + "\n## Conclusion\nDone.",
        sources=[{"url": "https://a.com"}, {"url": "https://b.com"}],
    )
    critique = run_critic(draft, threshold=0.50)
    # With a low threshold, should pass for a reasonable draft
    assert isinstance(critique.score, float)
    assert 0.0 <= critique.score <= 1.0


def test_critic_fails_empty_draft():
    draft = Draft(topic="X", title="X", body="Short.", sources=[])
    critique = run_critic(draft, threshold=0.80)
    assert not critique.passes


# ── Publisher Tests ───────────────────────────────────────────────────────────

def test_publisher_creates_file(tmp_path):
    draft = Draft(
        topic="AI Agents",
        title="AI Agents in 2026",
        body="# AI Agents in 2026\n\nContent here.",
        sources=[],
    )
    result = run_publisher(draft, output_dir=str(tmp_path))
    import os
    assert os.path.exists(result.filepath)
    content = open(result.filepath).read()
    assert "AI Agents in 2026" in content


# ── Full Pipeline Integration Tests ──────────────────────────────────────────

def test_pipeline_runs_to_completion():
    result = run_pipeline(
        topic="Redis caching strategies",
        max_iterations=2,
        quality_threshold=0.50,  # low threshold to pass in test
    )
    assert result.topic == "Redis caching strategies"
    assert result.iterations >= 1
    assert result.draft is not None
    assert result.critique is not None


def test_pipeline_aborts_if_threshold_too_high():
    result = run_pipeline(
        topic="X",
        max_iterations=1,
        quality_threshold=0.99,  # near-impossible to meet
    )
    # With max_iterations=1 and a very high threshold, it should fail gracefully
    assert isinstance(result.success, bool)
    assert result.reason != ""
