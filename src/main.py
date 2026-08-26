"""FastAPI entrypoint for the Autonomous Content Pipeline."""
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uvicorn

from src.pipeline import run_pipeline, PipelineResult

app = FastAPI(
    title="Autonomous Content Pipeline",
    description="Self-correcting multi-agent pipeline for researching and publishing content.",
    version="1.0.0",
)

_results: dict[str, PipelineResult] = {}


class PipelineRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Topic to research and write about")
    max_iterations: int = Field(3, ge=1, le=5)
    quality_threshold: float = Field(0.80, ge=0.5, le=1.0)


class PipelineStatusResponse(BaseModel):
    topic: str
    success: bool
    iterations: int
    reason: str
    score: float | None = None
    published_at: str | None = None
    filepath: str | None = None


@app.post("/api/v1/run", response_model=PipelineStatusResponse)
async def run(req: PipelineRequest):
    """Run the full pipeline synchronously and return the result."""
    result = run_pipeline(
        topic=req.topic,
        max_iterations=req.max_iterations,
        quality_threshold=req.quality_threshold,
    )
    return PipelineStatusResponse(
        topic=result.topic,
        success=result.success,
        iterations=result.iterations,
        reason=result.reason,
        score=result.critique.score if result.critique else None,
        published_at=result.publish.published_at if result.publish else None,
        filepath=result.publish.filepath if result.publish else None,
    )


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
