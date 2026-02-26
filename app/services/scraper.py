import httpx
from bs4 import BeautifulSoup

from app.logger import log


async def fetch_text(url: str) -> str:
    """
    Fetch the HTML at `url` and return its plain-text content.

    Returns:
        Plain text extracted from the page.

    Raises:
        httpx.HTTPStatusError  — if the server returns a 4xx/5xx response
        httpx.RequestError     — if the request itself fails (timeout, DNS, …)
    """
    async with httpx.AsyncClient() as client:
        log.info("fetching page", url=url)
        response = await client.get(url)
        response.raise_for_status()
        log.info("page fetched", url=url)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(["script", "style"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)
