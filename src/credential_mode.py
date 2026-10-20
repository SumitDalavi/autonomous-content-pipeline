import os

def is_live_openai_key(key: str | None = None) -> bool:
    """Check if a valid live OpenAI API key is supplied."""
    k = key if key is not None else os.getenv("OPENAI_API_KEY", "")
    return bool(k and k.startswith("sk-") and not k.startswith("sk-dummy") and len(k) >= 20)

def detect_mode() -> dict:
    return {
        "openai": "live" if is_live_openai_key() else "mock"
    }
