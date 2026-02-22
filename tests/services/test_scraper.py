from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services import scraper


@pytest.fixture
def mock_html_response():
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    return mock


async def test_returns_plain_text(mock_html_response):
    mock_html_response.text = "<html><body><p>Hello world</p></body></html>"
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_html_response)):
        result = await scraper.fetch_text("https://example.com")

        assert result == "Hello world"


async def test_strips_script_and_style_tags(mock_html_response):
    mock_html_response.text = """<html><head><style>body{}</style></head>
    <body><script>alert(1)</script><p>Real content</p></body></html>"""
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_html_response)):
        result = await scraper.fetch_text("https://example.com")

        assert result == "Real content"
        assert "alert" not in result
        assert "body{}" not in result


async def test_raises_http_error(mock_html_response):
    mock_html_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "error", request=MagicMock(), response=MagicMock()
    )
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_html_response)):
        with pytest.raises(httpx.HTTPStatusError):
            await scraper.fetch_text("https://example.com")
