from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import summary  # noqa: F401
from app.routes import summarize


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Distill",
    description="URL summarizer powered by a local LLM via Ollama.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(summarize.router)
