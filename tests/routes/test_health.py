from unittest.mock import AsyncMock, patch


def test_health_ok(client):
    with patch("app.services.ollama.check_health", new=AsyncMock(return_value=True)):
        response = client.get("/health")

    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "ok"
    assert data["db"] == "ok"
    assert data["ollama"] == "ok"


def test_health_db_unreachable(client, db_session):
    with patch.object(db_session, "execute", side_effect=Exception("DB down")):
        with patch(
            "app.services.ollama.check_health", new=AsyncMock(return_value=True)
        ):
            response = client.get("/health")

    data = response.json()
    assert response.status_code == 503
    assert data["status"] == "error"
    assert data["db"] == "unreachable"
    assert data["ollama"] == "ok"


def test_health_ollama_unreachable(client):
    with patch("app.services.ollama.check_health", new=AsyncMock(return_value=False)):
        response = client.get("/health")

    data = response.json()
    assert response.status_code == 503
    assert data["status"] == "error"
    assert data["db"] == "ok"
    assert data["ollama"] == "unreachable"
