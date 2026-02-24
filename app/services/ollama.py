import httpx

from app.config import settings
from app.schemas.summary import SummaryLength


async def check_health() -> bool:
    """
    Check if Ollama server is healthy.

    Returns True if healthy; False otherwise.
    """
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
        response.raise_for_status()
        return True
    except Exception:
        return False


async def summarize(text: str, length: SummaryLength = "medium") -> str:
    """
    Send `text` to the local Ollama instance and return the generated summary.

    Returns:
        The LLM-generated summary as a plain string.

    Raises:
        httpx.HTTPStatusError  — if Ollama returns an error response
        httpx.RequestError     — if the request to Ollama fails
    """
    length_prompt: dict[SummaryLength, str] = {
        "short": "1-2 sentences",
        "medium": "3-5 sentences",
        "long": "8-10 sentences",
    }
    prompt = f"""Summarize the following article in {length_prompt[length]}. 
    Return only the summary:\n\n{text}"""
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json()["response"]
