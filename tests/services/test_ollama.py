from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config import settings
from app.services import ollama


async def test_returns_summary_from_response():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"response": "This is the summary."}

    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
        result = await ollama.summarize("some long article text")

        assert result == "This is the summary."


async def test_sends_correct_payload():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"response": "This is the summary."}

    with patch(
        "httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)
    ) as mock_post:
        await ollama.summarize("article text")

        _, kwargs = mock_post.call_args
        assert kwargs["json"]["model"] == settings.ollama_model
        assert kwargs["json"]["stream"] is False
        assert "article text" in kwargs["json"]["prompt"]


async def test_raises_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=MagicMock()
    )
    with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
        with pytest.raises(httpx.HTTPStatusError):
            await ollama.summarize("article text")


async def test_healthy():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.status_code = 200

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await ollama.check_health()

        assert result is True


async def test_not_healthy():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=MagicMock()
    )
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await ollama.check_health()

        assert result is False
