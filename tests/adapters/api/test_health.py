"""
test_health.py
--------------
Tests for GET /health endpoint.

Uses FastAPI's TestClient (which wraps httpx) so we can make real HTTP
requests without starting a live server.
"""

from fastapi.testclient import TestClient

from src.adapters.api.main import app

# Create a test client that talks directly to our FastAPI app
client = TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_health_returns_200():
    """The /health endpoint must respond with HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_status_ok():
    """The /health response body must contain {"status": "ok"}."""
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
