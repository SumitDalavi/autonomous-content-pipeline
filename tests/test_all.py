import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os
import sys

# Mock openai
mock_openai_module = MagicMock()
mock_openai_client = MagicMock()
mock_openai_module.OpenAI.return_value = mock_openai_client
sys.modules["openai"] = mock_openai_module
os.environ["OPENAI_API_KEY"] = "fake-key"

# Mock tavily
mock_tavily_module = MagicMock()
mock_tavily_client = MagicMock()
mock_tavily_module.TavilyClient.return_value = mock_tavily_client
sys.modules["tavily"] = mock_tavily_module
os.environ["TAVILY_API_KEY"] = "fake-tavily"

# Mock httpx for search_tool
mock_httpx = MagicMock()
sys.modules["httpx"] = mock_httpx

from src.main import app
import src.agents.critic as critic
import src.agents.writer as writer
import src.tools.search_tool as search_tool
from src.agents.researcher import ResearchResult, run_researcher
from src.agents.writer import Draft
from src.agents.publisher import run_publisher
from src.pipeline import run_pipeline

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_pipeline_run():
    # We want to mock the LLM calls so the pipeline completes quickly
    
    # 1. Researcher mock
    search_tool._TAVILY_AVAILABLE = True
    mock_tavily_client.search.return_value = {
        "results": [
            {"title": "Test", "url": "http://test.com", "content": "Test content"}
        ]
    }
    mock_resp = MagicMock()
    mock_resp.text = "<p>Test html text</p>"
    mock_httpx.get.return_value = mock_resp
    
    # Mock LLMs for writer and critic
    writer._LLM_AVAILABLE = True
    critic._LLM_AVAILABLE = True

    # Writer LLM Mock
    mock_writer_resp = MagicMock()
    mock_writer_resp.choices = [MagicMock(message=MagicMock(content="# Test Title\n\nTest Body"))]
    
    # Critic LLM Mock
    mock_critic_resp = MagicMock()
    mock_critic_resp.choices = [MagicMock(message=MagicMock(content='{"score": 0.9, "strengths": ["s1"], "feedback": ["f1"]}'))]
    
    def mock_create(*args, **kwargs):
        content = kwargs.get("messages", [{}])[0].get("content", "").lower()
        if "writer" in content or "write a well-structured" in content:
            return mock_writer_resp
        return mock_critic_resp
    
    mock_openai_client.chat.completions.create.side_effect = mock_create
    
    res = client.post("/api/v1/run", json={"topic": "Artificial Intelligence", "max_iterations": 1, "quality_threshold": 0.5})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["score"] == 0.9

def test_pipeline_failure():
    # Test when critic fails continually
    search_tool._TAVILY_AVAILABLE = False
    
    writer._LLM_AVAILABLE = False
    critic._LLM_AVAILABLE = False
    
    # Draft created by heuristic writer, let's see if critic rejects it
    with patch("src.pipeline.run_critic") as mock_run_critic:
        mock_run_critic.return_value = critic.CritiqueResult(score=0.1, passes=False, feedback=["bad"])
        res = client.post("/api/v1/run", json={"topic": "Bad Topic", "max_iterations": 1, "quality_threshold": 0.9})
        assert res.status_code == 200
        assert res.json()["success"] is False
        assert "not met" in res.json()["reason"]

def test_pipeline_no_critique():
    # Test when critic fails continually
    search_tool._TAVILY_AVAILABLE = False
    
    writer._LLM_AVAILABLE = False
    critic._LLM_AVAILABLE = False
    
    # Draft created by heuristic writer, let's see if critic rejects it
    with patch("src.pipeline.run_critic") as mock_run_critic:
        mock_run_critic.return_value = None
        # Actually it's easier to just patch run_pipeline with threshold
        from src.pipeline import run_pipeline
        res = run_pipeline("topic", max_iterations=0)
        assert res.success is False
        assert "No critique produced" in res.reason

def test_writer_fallback():
    writer._LLM_AVAILABLE = False
    draft = writer.run_writer(ResearchResult("topic", [{"url": "http://mock"}], "summary", ["f1"]))
    assert draft.word_count > 0
    assert "The Complete Guide to Topic" in draft.title
    writer._LLM_AVAILABLE = True

def test_critic_fallback():
    critic._LLM_AVAILABLE = False
    draft = Draft("topic", "title", "## " + "body "*600, sources=[{"url": "http://1"}, {"url": "http://2"}])
    res = critic.run_critic(draft, 0.5)
    assert res.score > 0
    assert res.passes is True
    critic._LLM_AVAILABLE = True

def test_critic_llm_json_error():
    critic._LLM_AVAILABLE = True
    mock_critic_resp = MagicMock()
    mock_critic_resp.choices = [MagicMock(message=MagicMock(content='bad json'))]
    mock_openai_client.chat.completions.create.side_effect = [mock_critic_resp]
    
    draft = Draft("topic", "title", "body", sources=[])
    res = critic.run_critic(draft, 0.5)
    assert res.score == 0.0  # From heuristic fallback
    mock_openai_client.chat.completions.create.side_effect = None

def test_search_tool_fallback():
    search_tool._TAVILY_AVAILABLE = False
    res = search_tool.web_search("query")
    assert len(res) == 1
    assert "Mock result" in res[0]["title"]
    search_tool._TAVILY_AVAILABLE = True

def test_fetch_url_error():
    mock_httpx.get.side_effect = Exception("error")
    res = search_tool.fetch_url("http://err.com")
    assert "fetch error" in res
    mock_httpx.get.side_effect = None

def test_researcher(tmp_path):
    # run researcher
    search_tool._TAVILY_AVAILABLE = False
    res = run_researcher("test topic", depth=1)
    assert res.topic == "test topic"
    assert len(res.sources) == 1

def test_publisher(tmp_path):
    draft = Draft("topic", "title", "body text")
    res = run_publisher(draft, str(tmp_path))
    assert res.filepath.endswith(".md")
    assert os.path.exists(res.filepath)
