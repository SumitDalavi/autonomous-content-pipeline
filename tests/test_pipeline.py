import os
import pytest
from src.pipeline import ContentPipeline

def test_fetch_data():
    pipeline = ContentPipeline("test topic")
    data = pipeline.fetch_data()
    assert len(data) == 2
    assert "mock_api_1" in data[0]["source"]

def test_generate_content():
    pipeline = ContentPipeline("test topic")
    mock_data = [{"source": "test_src", "content": "test_data"}]
    content = pipeline.generate_content(mock_data)
    assert "test topic".title() in content
    assert "test_data" in content

def test_save_output(tmp_path):
    pipeline = ContentPipeline("test topic")
    # Override output dir to use pytest temp dir
    pipeline.output_dir = str(tmp_path)
    
    filepath = pipeline.save_output("dummy content")
    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        assert f.read() == "dummy content"
