import httpx

from app.config import settings
from app.logger import log
from app.schemas.summary import SummaryFormat, SummaryLength


async def check_health() -> bool:
    """
    Check if Ollama server is healthy.

    Returns True if healthy; False otherwise.
    """
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            log.info("check ollama health")
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
        response.raise_for_status()
        log.info("ollama is healthy")
        return True
    except Exception:
        log.info("ollama is not healthy")
        return False


async def summarize(
    text: str, length: SummaryLength = "medium", format: SummaryFormat = "prose"
) -> str:
    """
    Send `text` to the local Ollama instance and return the generated summary.

    Returns:
        The LLM-generated summary as a plain string.

    Raises:
        httpx.HTTPStatusError  — if Ollama returns an error response
        httpx.RequestError     — if the request to Ollama fails
    """
    LENGTH_MAP: dict[SummaryLength, str] = {
        "short": "1-2",
        "medium": "3-5",
        "long": "8-10",
    }
    PROMPTS: dict[SummaryFormat, str] = {
        "prose": """Summarize the following article in {n} sentences. 
                Return only the summary:""",
        "markdown": """Summarize the following article as Markdown with a bold title 
                and {n} bullet points. Return only the Markdown:""",
    }
    prompt = f"{PROMPTS[format].format(n=LENGTH_MAP[length])}\n\n{text}"
    async with httpx.AsyncClient(timeout=120) as client:
        log.info("summarizing", model=settings.ollama_model)
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        log.info("summarization complete", model=settings.ollama_model)
        return response.json()["response"]
