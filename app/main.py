from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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


@app.exception_handler(httpx.HTTPStatusError)
async def http_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    return JSONResponse(
        status_code=422,
        content={"detail": f"Failed to fetch URL: {exc.response.status_code}"},
    )


@app.exception_handler(httpx.RequestError)
async def request_error_handler(request: Request, exc: httpx.RequestError):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Could not reach an external service. Please try again later."
        },
    )
