"""
remoteok.py
-----------
Fetches jobs from the public RemoteOK API and maps them into SkillPulse's
raw job dictionary shape.

This module only handles ingestion. It does not clean text, extract skills,
count skills, call the database, or update the dashboard/API.
"""

from datetime import datetime, timezone

import httpx


REMOTEOK_API_URL = "https://remoteok.com/api"


def format_remoteok_date(job: dict) -> str | None:
    """
    Convert RemoteOK date fields into YYYY-MM-DD when possible.

    Input:
        job (dict): One raw RemoteOK job record.

    Output:
        str | None: A date string like "2026-05-23", or None if unavailable.
    """
    date_value = job.get("date")
    if isinstance(date_value, str) and len(date_value) >= 10:
        return date_value[:10]

    epoch_value = job.get("epoch") or job.get("date_epoch")
    if isinstance(epoch_value, int):
        return datetime.fromtimestamp(epoch_value, tz=timezone.utc).date().isoformat()

    return None


def infer_seniority(title: str) -> str:
    """
    Infer a simple seniority value from the job title.

    Input:
        title (str): RemoteOK position/title field.

    Output:
        str: "junior", "senior", or "" when no simple signal is found.
    """
    title = title.lower()

    if "junior" in title or "entry" in title:
        return "junior"

    if "senior" in title or "sr." in title or "lead" in title:
        return "senior"

    return ""


def normalize_remoteok_job(remoteok_job: dict) -> dict:
    """
    Map one RemoteOK record into the existing SkillPulse raw job shape.

    Input:
        remoteok_job (dict): One job record returned by the RemoteOK API.

    Output:
        dict: A raw job dictionary with the same keys as sample_jobs.json.
    """
    job_id = remoteok_job.get("id")
    title = remoteok_job.get("position") or remoteok_job.get("title") or ""
    tags = remoteok_job.get("tags") or []

    if not isinstance(tags, list):
        tags = []

    return {
        "id": f"remoteok_{job_id}" if job_id is not None else None,
        "title": title,
        "company": remoteok_job.get("company") or "",
        "description": remoteok_job.get("description") or "",
        "location": remoteok_job.get("location") or "Remote",
        "remote_type": "remote",
        "source": "remoteok",
        "source_url": remoteok_job.get("url") or f"https://remoteok.com/remote-jobs/{job_id}",
        "posted_at": format_remoteok_date(remoteok_job),
        "employment_type": remoteok_job.get("employment_type") or remoteok_job.get("type") or "",
        "seniority": infer_seniority(title),
        "tags": tags,
    }


def fetch_remoteok_jobs(limit: int | None = None, client: httpx.Client | None = None) -> list[dict]:
    """
    Fetch RemoteOK jobs and return SkillPulse-shaped raw job dictionaries.

    Input:
        limit (int | None): Optional maximum number of jobs to return.
        client (httpx.Client | None): Optional client used by tests to avoid
            live network calls.

    Output:
        list[dict]: RemoteOK jobs converted into the existing raw job shape.

    Edge cases:
        - Network/request failure: raises RuntimeError with a clear message.
        - Non-2xx response: raises RuntimeError with a clear message.
        - Unexpected JSON shape: raises ValueError.
        - RemoteOK metadata rows are skipped.
    """
    http_client = client or httpx.Client(timeout=10)
    should_close_client = client is None

    try:
        response = http_client.get(REMOTEOK_API_URL)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Failed to fetch RemoteOK jobs: {exc}") from exc
    finally:
        if should_close_client:
            http_client.close()

    if not isinstance(data, list):
        raise ValueError(f"Expected RemoteOK API to return a list, got {type(data).__name__}")

    normalized_jobs = []

    for item in data:
        if not isinstance(item, dict):
            continue

        if "id" not in item or ("position" not in item and "title" not in item):
            continue

        normalized_jobs.append(normalize_remoteok_job(item))

        if limit is not None and len(normalized_jobs) >= limit:
            break

    return normalized_jobs
