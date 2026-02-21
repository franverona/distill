async def fetch_text(url: str) -> str:
    """
    Fetch the HTML at `url` and return its plain-text content.

    Steps to implement:
        1. Use httpx.AsyncClient to send a GET request to `url`
        2. Raise an exception if the response status is not 2xx
           Hint: response.raise_for_status()
        3. Parse the HTML with BeautifulSoup (parser: "html.parser")
        4. Extract readable text — consider removing <script> and <style> tags
           before calling .get_text()
        5. Strip excessive whitespace and return the cleaned string

    Returns:
        Plain text extracted from the page.

    Raises:
        httpx.HTTPStatusError  — if the server returns a 4xx/5xx response
        httpx.RequestError     — if the request itself fails (timeout, DNS, …)
    """
    # TODO: Implement the steps above
    pass
