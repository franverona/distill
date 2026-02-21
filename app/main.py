from fastapi import FastAPI

from app.routes import summarize

app = FastAPI(
    title="Distill",
    description="URL summarizer powered by a local LLM via Ollama.",
    version="0.1.0",
)

# TODO: Register the summarize router on the app instance
# Hint: use app.include_router(...)
