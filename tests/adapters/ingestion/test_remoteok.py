"""
test_remoteok.py
----------------
Tests for the RemoteOK ingestion adapter.

These tests do not call the live RemoteOK API. They use fake clients and
sample payloads so the test suite stays fast and deterministic.
"""

import httpx
import pytest

from src.adapters.ingestion.remoteok import fetch_remoteok_jobs, normalize_remoteok_job


class FakeResponse:
    """Small fake HTTP response used by RemoteOK ingestion tests."""

    def __init__(self, data, status_code: int = 200):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "bad response",
                request=httpx.Request("GET", "https://remoteok.com/api"),
                response=httpx.Response(self.status_code),
            )

    def json(self):
        return self._data


class FakeClient:
    """Small fake HTTP client used to avoid live network calls."""

    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error

    def get(self, url: str):
        if self.error:
            raise self.error

        return FakeResponse(self.data)


def test_normalize_remoteok_job_maps_expected_fields():
    """RemoteOK records should become SkillPulse raw job dictionaries."""
    remoteok_job = {
        "id": 12345,
        "position": "Senior Data Engineer",
        "company": "Remote Data Co",
        "description": "Build pipelines with Python, SQL, and Airflow.",
        "location": "Worldwide",
        "url": "https://remoteok.com/remote-jobs/12345",
        "date": "2026-05-20T12:00:00+00:00",
        "tags": ["python", "sql", "airflow"],
    }

    job = normalize_remoteok_job(remoteok_job)

    assert job == {
        "id": "remoteok_12345",
        "title": "Senior Data Engineer",
        "company": "Remote Data Co",
        "description": "Build pipelines with Python, SQL, and Airflow.",
        "location": "Worldwide",
        "remote_type": "remote",
        "source": "remoteok",
        "source_url": "https://remoteok.com/remote-jobs/12345",
        "posted_at": "2026-05-20",
        "employment_type": "",
        "seniority": "senior",
        "tags": ["python", "sql", "airflow"],
    }


def test_fetch_remoteok_jobs_skips_metadata_and_applies_limit():
    """RemoteOK metadata rows should be skipped before applying the limit."""
    payload = [
        {"legal": "metadata row"},
        {
            "id": 1,
            "position": "Python Engineer",
            "company": "One",
            "description": "Python work",
            "tags": ["python"],
        },
        {
            "id": 2,
            "position": "SQL Analyst",
            "company": "Two",
            "description": "SQL work",
            "tags": ["sql"],
        },
    ]
    client = FakeClient(data=payload)

    jobs = fetch_remoteok_jobs(limit=1, client=client)

    assert len(jobs) == 1
    assert jobs[0]["id"] == "remoteok_1"
    assert jobs[0]["source"] == "remoteok"


def test_fetch_remoteok_jobs_raises_runtime_error_on_network_failure():
    """Network errors should become clear RuntimeError exceptions."""
    client = FakeClient(error=httpx.RequestError("connection failed"))

    with pytest.raises(RuntimeError, match="Failed to fetch RemoteOK jobs"):
        fetch_remoteok_jobs(client=client)
