# TODO: Import settings from app.config to read OLLAMA_BASE_URL and OLLAMA_MODEL


async def summarize(text: str) -> str:
    """
    Send `text` to the local Ollama instance and return the generated summary.

    Steps to implement:
        1. Build a prompt asking the model to summarise the provided text
           Example: "Summarize the following article in 3-5 sentences:\\n\\n{text}"
        2. POST to {OLLAMA_BASE_URL}/api/generate with a JSON body:
              { "model": OLLAMA_MODEL, "prompt": "...", "stream": false }
        3. Parse the JSON response and extract the "response" field
        4. Return the summary string

    Returns:
        The LLM-generated summary as a plain string.

    Raises:
        httpx.HTTPStatusError  — if Ollama returns an error response
        httpx.RequestError     — if the request to Ollama fails
    """
    # TODO: Implement the steps above
    pass
