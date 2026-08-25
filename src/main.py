from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class ContentRequest(BaseModel):
    topic: str
    target_audience: str

def generate_content(req: ContentRequest) -> dict:
    # Mocking CrewAI / LangChain agent execution
    # E.g. Researcher agent -> Writer agent -> Editor agent
    return {
        "title": f"The Ultimate Guide to {req.topic}",
        "body": f"Welcome, {req.target_audience}! Here is everything you need to know about {req.topic}...",
        "status": "published"
    }

@app.post("/generate")
async def generate(req: ContentRequest):
    return generate_content(req)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
