from unittest.mock import AsyncMock, patch

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


def test_get_summarize_history_id_not_found(client, db_session):
    response = client.get("/summarize/history/9999")

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "Not found"
