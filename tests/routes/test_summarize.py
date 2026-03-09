import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config import settings
from app.repositories import summary as summary_repo


@pytest.mark.parametrize("length", ["short", "medium", "long"])
def test_post_summarize_success_lengths(client, db_session, length):
    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value="article text")
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="the summary")
        ):
            response = client.post(
                "/summarize", json={"url": "https://example.com", "length": length}
            )

    assert response.status_code == 201
    assert response.json()["summary"] == "the summary"
    assert response.json()["url"] == "https://example.com/"
    record_id = response.json()["id"]
    record = summary_repo.get_by_id(db_session, record_id)
    assert record is not None
    assert record.content == "article text"


def test_post_summarize_invalid_length(client):
    response = client.post(
        "/summarize", json={"url": "https://example.com", "length": "tiny"}
    )

    assert response.status_code == 422


def test_post_summarize_invalid_url(client):
    response = client.post("/summarize", json={"url": "not-a-url"})

    assert response.status_code == 422


def test_get_summarize_history_list(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    response = client.get("/summarize/history")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total"] == 1
    assert data["prev"] is None
    assert data["next"] is None


def test_get_summarize_history_list_with_query(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://python.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    response = client.get("/summarize/history?q=python")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total"] == 1
    assert data["prev"] is None
    assert data["next"] is None


def test_get_summarize_history_list_first_page(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    response = client.get("/summarize/history?size=1&page=1")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["page"] == 1
    assert data["size"] == 1
    assert data["total"] == 3
    assert data["prev"] is None
    assert data["next"] == "/summarize/history?size=1&page=2"


def test_get_summarize_history_list_middle_page(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    response = client.get("/summarize/history?page=2&size=1")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["page"] == 2
    assert data["size"] == 1
    assert data["total"] == 3
    assert data["prev"] == "/summarize/history?size=1&page=1"
    assert data["next"] == "/summarize/history?size=1&page=3"


def test_get_summarize_history_list_last_page(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    response = client.get("/summarize/history?page=3&size=1")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["page"] == 3
    assert data["size"] == 1
    assert data["total"] == 3
    assert data["prev"] == "/summarize/history?size=1&page=2"
    assert data["next"] is None


def test_get_summarize_history_list_query_next_prev(client, db_session):
    summary_repo.create(
        db_session,
        url="https://python.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://python.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://python.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    response = client.get("/summarize/history?size=1&q=python&page=2")

    data = response.json()
    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["page"] == 2
    assert data["size"] == 1
    assert data["total"] == 3
    assert data["prev"] == "/summarize/history?size=1&q=python&page=1"
    assert data["next"] == "/summarize/history?size=1&q=python&page=3"


def test_get_summarize_history_id_success(client, db_session):
    record = summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
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
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
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
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    client.delete(f"/summarize/history/{record.id}")
    response = client.get(f"/summarize/history/{record.id}")

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "Not found"


def test_retry_summary_not_found(client):
    response = client.post("/summarize/history/9999/retry")

    data = response.json()
    assert response.status_code == 404
    assert data["detail"] == "Not found"


def test_retry_summary_success(client, db_session):
    record = summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value="article text")
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="the summary")
        ):
            response = client.post(f"/summarize/history/{record.id}/retry")

    assert response.status_code == 200
    assert response.json()["summary"] == "the summary"
    assert response.json()["url"] == "https://example.com"
    record_id = response.json()["id"]
    record = summary_repo.get_by_id(db_session, record_id)
    assert record is not None
    assert record.content == "article text"


def test_post_summarize_truncates_long_content(client):
    long_text = "a" * 100_000

    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value=long_text)
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="the summary")
        ) as mock_ollama:
            client.post("/summarize", json={"url": "https://example.com"})

    actual_text = mock_ollama.call_args.kwargs["text"]
    assert len(actual_text) == 50_000


def test_retry_summarize_truncates_long_content(client, db_session):
    record = summary_repo.create(
        db_session,
        url="https://example.com",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    long_text = "a" * 100_000

    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value=long_text)
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="the summary")
        ) as mock_ollama:
            client.post(f"/summarize/history/{record.id}/retry")

    actual_text = mock_ollama.call_args.kwargs["text"]
    assert len(actual_text) == 50_000


def test_post_summarize_returns_reading_time(client):
    # 400 words → 2 minutes at 200 wpm
    text = "word " * 400

    with patch("app.services.scraper.fetch_text", new=AsyncMock(return_value=text)):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
        ):
            response = client.post("/summarize", json={"url": "https://example.com"})

    assert response.json()["reading_time_minutes"] == 2


def test_response_has_request_id_header(client):
    response = client.get("/summarize/history")
    assert "x-request-id" in response.headers


def test_export_csv(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com",
        content="c",
        summary="s",
        model="llama3.2",
        length="medium",
        format="prose",
    )
    response = client.get("/summarize/history/export")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "url" in response.text  # header row
    assert "example.com" in response.text


def test_export_jsonl(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com",
        content="c",
        summary="s",
        model="llama3.2",
        length="medium",
        format="prose",
    )
    response = client.get("/summarize/history/export?format=jsonl")

    assert response.status_code == 200
    lines = [line for line in response.text.strip().split("\n") if line]
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["url"] == "https://example.com"


def test_export_empty_db(client):
    response = client.get("/summarize/history/export")

    assert response.status_code == 200
    lines = response.text.strip().split("\n")
    assert len(lines) == 1  # only the header row


def test_blocked_domain_rejected(client, monkeypatch):
    monkeypatch.setattr(settings, "url_blocklist", "evil.com")
    with patch("app.schemas.summary.socket.gethostbyname", return_value="1.2.3.4"):
        response = client.post("/summarize", json={"url": "http://evil.com/page"})
    assert response.status_code == 422


def test_allowlist_permits_listed_domain(client, monkeypatch):
    monkeypatch.setattr(settings, "url_allowlist", "allowed.com")
    with patch("app.schemas.summary.socket.gethostbyname", return_value="1.2.3.4"):
        with patch(
            "app.services.scraper.fetch_text", new=AsyncMock(return_value="text")
        ):
            with patch(
                "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
            ):
                response = client.post(
                    "/summarize", json={"url": "http://allowed.com/page"}
                )
    assert response.status_code == 201


def test_allowlist_rejects_unlisted_domain(client, monkeypatch):
    monkeypatch.setattr(settings, "url_allowlist", "allowed.com")
    with patch("app.schemas.summary.socket.gethostbyname", return_value="1.2.3.4"):
        response = client.post(
            "/summarize", json={"url": "http://not-allowed.com/page"}
        )
    assert response.status_code == 422


def test_url_validation_localhost(client):
    response = client.post("/summarize", json={"url": "http://localhost/page"})

    assert response.status_code == 422


def test_url_validation_localhost_ip(client):
    response = client.post("/summarize", json={"url": "http://127.0.0.1/page"})

    assert response.status_code == 422


def test_url_validation_local_ip(client):
    response = client.post("/summarize", json={"url": "http://192.168.1.1/page"})

    assert response.status_code == 422


def test_request_without_key_returns_401(client, monkeypatch):
    monkeypatch.setattr(settings, "api_key", "secret")
    response = client.post("/summarize", json={"url": "http://example.com/page"})

    assert response.status_code == 401


def test_request_with_wrong_key_returns_401(client, monkeypatch):
    monkeypatch.setattr(settings, "api_key", "secret")
    response = client.post(
        "/summarize",
        json={"url": "http://example.com/page"},
        headers={"X-API-Key": "other-secret"},
    )

    assert response.status_code == 401


def test_request_with_correct_key_succeeds(client, monkeypatch):
    monkeypatch.setattr(settings, "api_key", "secret")

    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value="some text")
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
        ):
            response = client.post(
                "/summarize",
                json={"url": "https://example.com"},
                headers={"X-API-Key": "secret"},
            )

    assert response.status_code == 201


def test_auth_disabled_when_key_is_empty(client, monkeypatch):
    monkeypatch.setattr(settings, "api_key", None)
    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value="some text")
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
        ):
            response = client.post("/summarize", json={"url": "https://example.com"})

    assert response.status_code == 201


def test_batch_summarize_all_success(client):
    with patch(
        "app.services.scraper.fetch_text", new=AsyncMock(return_value="some text")
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
        ):
            response = client.post(
                "/summarize/batch",
                json={"urls": ["https://example-1.com", "https://example-2.com"]},
            )

    assert response.status_code == 200


def test_batch_summarize_partial_failure(client):
    pass


def test_batch_exceeds_max_size_returns_422(client):
    with patch(
        "app.services.scraper.fetch_text",
        new=AsyncMock(side_effect=["some text", httpx.RequestError("timeout")]),
    ):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
        ):
            response = client.post(
                "/summarize/batch",
                json={
                    "urls": [
                        "https://example-1.com",
                        "https://example-2.com",
                    ]
                },
            )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["success"] is True
    assert results[1]["success"] is False
    assert "timeout" in results[1]["error"]


def test_post_summarize_cache_miss(client):
    with patch("app.services.scraper.fetch_text", new=AsyncMock(return_value="text")):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
        ):
            response = client.post("/summarize", json={"url": "https://example.com/"})

    assert response.status_code == 201
    assert response.headers["x-cache"] == "MISS"


def test_post_summarize_cache_miss_outdated(client, db_session):
    record = summary_repo.create(
        db_session,
        url="https://example.com/",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    # Force the record to look old
    record.created_at = datetime(2020, 1, 1)
    db_session.commit()

    with patch("app.services.scraper.fetch_text", new=AsyncMock(return_value="text")):
        with patch(
            "app.services.ollama.summarize", new=AsyncMock(return_value="summary")
        ):
            response = client.post("/summarize", json={"url": "https://example.com/"})

    assert response.status_code == 201
    assert response.headers["x-cache"] == "MISS"
    assert response.json()["summary"] == "summary"


def test_post_summarize_cache_hit(client, db_session):
    summary_repo.create(
        db_session,
        url="https://example.com/",
        summary="A summary",
        content="A content",
        model="llama3.2",
    )
    response = client.post("/summarize", json={"url": "https://example.com/"})

    assert response.status_code == 200
    assert response.headers["x-cache"] == "HIT"
    assert response.json()["summary"] == "A summary"
