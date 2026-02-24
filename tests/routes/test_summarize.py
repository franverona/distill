from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from app.repositories import summary as summary_repo


def test_post_summarize_success(client):
    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value="article text")
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="the summary")
        ):
            response = client.post("/summarize", json={"url": "https://example.com"})

    assert response.status_code == 201
    assert response.json()["summary"] == "the summary"
    assert response.json()["url"] == "https://example.com/"


def test_post_summarize_invalid_url(client):
    response = client.post("/summarize", json={"url": "not-a-url"})

    assert response.status_code == 422


def test_get_summarize_history_list(client, db_session):
    summary_repo.create(
        db_session, url="https://example.com", summary="A summary", model="llama3.2"
    )
    response = client.get("/summarize/history")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total"] == 1


def test_get_summarize_history_id_success(client, db_session):
    record = summary_repo.create(
        db_session, url="https://example.com", summary="A summary", model="llama3.2"
    )
    response = client.get(f"/summarize/history/{record.id}")

    data = response.json()
    assert response.status_code == 200
    assert data["summary"] == "A summary"
    assert data["url"] == "https://example.com"
    assert "id" in data
    assert "created_at" in data


def test_get_summarize_history_id_not_found(client):
    response = client.get("/summarize/history/9999")

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "Not found"


def test_post_summarize_scraper_error(client):
    with patch(
        "app.services.scraper.fetch_text",
        new=AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "error", request=MagicMock(), response=MagicMock(status_code=404)
            )
        ),
    ):
        response = client.post("/summarize", json={"url": "https://example.com"})

    assert response.status_code == 422


def test_post_summarize_ollama_error(client):
    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value="article text")
    ):
        with patch(
            "app.services.ollama.summarize",
            new=AsyncMock(side_effect=httpx.RequestError("connection failed")),
        ):
            response = client.post("/summarize", json={"url": "https://example.com"})

    assert response.status_code == 503


def test_delete_summarize_history_id_success(client, db_session):
    record = summary_repo.create(
        db_session, url="https://example.com", summary="A summary", model="llama3.2"
    )
    response = client.delete(f"/summarize/history/{record.id}")

    assert response.status_code == 204


def test_delete_summarize_history_id_not_found(client):
    response = client.delete("/summarize/history/9999")

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "Not found"


def test_delete_summarize_history_id_subsequent_get(client, db_session):
    record = summary_repo.create(
        db_session, url="https://example.com", summary="A summary", model="llama3.2"
    )
    client.delete(f"/summarize/history/{record.id}")
    response = client.get(f"/summarize/history/{record.id}")

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "Not found"


def test_url_validation_localhost(client):
    response = client.post("/summarize", json={"url": "http://localhost/page"})

    assert response.status_code == 422


def test_url_validation_localhost_ip(client):
    response = client.post("/summarize", json={"url": "http://127.0.0.1/page"})

    assert response.status_code == 422


def test_url_validation_local_ip(client):
    response = client.post("/summarize", json={"url": "http://192.168.1.1/page"})

    assert response.status_code == 422
