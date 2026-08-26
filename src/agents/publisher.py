"""Publisher agent: saves approved content to disk (or external platform)."""
from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.agents.writer import Draft


@dataclass
class PublishResult:
    filepath: str
    title: str
    word_count: int
    published_at: str


def run_publisher(draft: Draft, output_dir: str = "output") -> PublishResult:
    """
    Publish an approved draft as a Markdown file.
    In production this would push to Ghost/Dev.to/Notion via API.
    """
    print(f"[publisher] Publishing: {draft.title!r}")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    slug = draft.topic.lower().replace(" ", "-").replace("/", "-")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{slug}.md"
    filepath = os.path.join(output_dir, filename)

    metadata = f"""---
title: "{draft.title}"
topic: "{draft.topic}"
published_at: "{datetime.utcnow().isoformat()}Z"
word_count: {draft.word_count}
sources: {len(draft.sources)}
---

"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(metadata + draft.body)

    print(f"[publisher] Saved to {filepath} ({draft.word_count} words)")
    return PublishResult(
        filepath=filepath,
        title=draft.title,
        word_count=draft.word_count,
        published_at=datetime.utcnow().isoformat() + "Z",
    )
