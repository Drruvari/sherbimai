from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["services"] >= 8


def test_ask_returns_grounded_service():
    response = client.post("/api/ask", json={"question": "Sa kushton rinovimi ADR?"})
    assert response.status_code == 200
    body = response.json()
    assert body["matched"] is True
    assert body["service"]["id"] == "adr-renewal"
    assert "6500" in body["answer"]
    assert body["service"]["source_url"].startswith("https://")


def test_service_not_found():
    response = client.get("/api/services/does-not-exist")
    assert response.status_code == 404
