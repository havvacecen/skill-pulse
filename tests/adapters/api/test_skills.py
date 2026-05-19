"""
test_skills.py
--------------
Tests for GET /skills endpoint.

Uses FastAPI's TestClient (no live server needed).
Tests cover the happy path, the top_n query parameter, and the valid range.
"""

from fastapi.testclient import TestClient

from src.adapters.api.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_skills_returns_200():
    """The /skills endpoint must respond with HTTP 200."""
    response = client.get("/skills")
    assert response.status_code == 200


def test_skills_response_has_skills_key():
    """The response JSON must contain a top-level 'skills' key."""
    response = client.get("/skills")
    data = response.json()
    assert "skills" in data


def test_skills_items_have_correct_shape():
    """Each item in 'skills' must have 'skill' (str) and 'count' (int) keys."""
    response = client.get("/skills")
    skills = response.json()["skills"]
    for item in skills:
        assert "skill" in item
        assert "count" in item
        assert isinstance(item["skill"], str)
        assert isinstance(item["count"], int)


def test_skills_top_n_limits_results():
    """?top_n=3 must return at most 3 items."""
    response = client.get("/skills?top_n=3")
    assert response.status_code == 200
    skills = response.json()["skills"]
    assert len(skills) <= 3


def test_skills_default_top_n_is_ten():
    """Without ?top_n the response must return at most 10 items."""
    response = client.get("/skills")
    skills = response.json()["skills"]
    assert len(skills) <= 10


def test_skills_top_n_zero_returns_422():
    """?top_n=0 is below the minimum (ge=1) and must return HTTP 422."""
    response = client.get("/skills?top_n=0")
    assert response.status_code == 422


def test_skills_top_n_above_max_returns_422():
    """?top_n=101 exceeds the maximum (le=100) and must return HTTP 422."""
    response = client.get("/skills?top_n=101")
    assert response.status_code == 422


def test_skills_sorted_descending():
    """Skills must be ordered from highest count to lowest."""
    response = client.get("/skills")
    skills = response.json()["skills"]
    counts = [item["count"] for item in skills]
    assert counts == sorted(counts, reverse=True)
