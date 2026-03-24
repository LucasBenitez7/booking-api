import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_client() -> TestClient:
    from booking.api.main import app

    with TestClient(app) as client:
        yield client


def test_health_returns_ok(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_health_ready_returns_ready(api_client: TestClient) -> None:
    response = api_client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
