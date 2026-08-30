from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_validation() -> None:
    response = client.post("/query", json={"question": "hi", "top_k": 4})
    assert response.status_code == 422


def test_reject_non_pdf() -> None:
    response = client.post(
        "/documents",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
