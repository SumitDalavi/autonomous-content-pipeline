from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from main import app

client = TestClient(app)

def test_generate_content():
    response = client.post("/generate", json={"topic": "AI", "target_audience": "Devs"})
    assert response.status_code == 200
    assert "AI" in response.json()["title"]
    assert "Devs" in response.json()["body"]
    assert response.json()["status"] == "published"
