"""
skills.py
---------
Defines the source-aware /skills endpoint for the SkillPulse API.

Purpose:
    Supports sample and RemoteOK data sources, runs the full SkillPulse
    pipeline in memory, and returns the top N most-demanded skills.

Endpoint:
    GET /skills?source=sample&top_n=10
    Response: {"skills": [{"skill": "python", "count": 8}, ...]}

Pipeline steps performed on each request:
    1. Load raw jobs from the selected source   (ingestion)
    2. Clean each job            (cleaning)
    3. Extract skills per job    (skill_extraction)
    4. Count & sort skills       (skill_counts)

Constraints:
    - No database
    - No authentication
    - Synchronous (no async)
    - Data file path resolved relative to the project root via Path
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from src.adapters.ingestion.ingestion import load_jobs
from src.adapters.ingestion.remoteok import fetch_remoteok_jobs
from src.core.pipeline.cleaning import clean_job
from src.core.pipeline.skill_extraction import enrich_job_with_skills
from src.core.analytics.skill_counts import get_skill_counts

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Resolved once at import time so the path is always correct regardless of
# where uvicorn is started from.
_PROJECT_ROOT = Path(__file__).resolve().parents[4]  # up to skill-pulse/
_SAMPLE_DATA_PATH = _PROJECT_ROOT / "data" / "raw" / "sample_jobs.json"
SUPPORTED_SOURCES = ("sample", "remoteok")

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


# ---------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------

def load_raw_jobs_for_source(source: str) -> list[dict]:
    """
    Load raw jobs from the selected source.

    Input:
        source (str): "sample" or "remoteok".

    Output:
        list[dict]: Raw job dictionaries in the SkillPulse job shape.

    Edge cases:
        - Unknown source raises ValueError.
        - Missing sample file raises FileNotFoundError.
        - RemoteOK request failure raises RuntimeError.
    """
    normalized_source = source.lower()

    if normalized_source == "sample":
        return load_jobs(str(_SAMPLE_DATA_PATH))

    if normalized_source == "remoteok":
        return fetch_remoteok_jobs()

    raise ValueError(
        f"Unsupported source '{source}'. Supported sources: {', '.join(SUPPORTED_SOURCES)}"
    )


# ---------------------------------------------------------------------------
# GET /skills
# ---------------------------------------------------------------------------

@router.get("/skills")
def get_top_skills(
    top_n: int = Query(default=10, ge=1, le=100, description="Number of top skills to return"),
    source: str = Query(default="sample", description="Job data source: sample or remoteok"),
) -> dict:
    """
    Return the most frequently mentioned skills in the selected job dataset.

    Query parameters:
        top_n (int): How many skills to include in the response.
                     Must be between 1 and 100. Defaults to 10.
        source (str): Which raw data source to use. Defaults to "sample".

    Input:  query param ?top_n=<int>
    Output: {"skills": [{"skill": "python", "count": 8}, ...]}

    Pipeline executed on every call (no caching in Phase 1):
        load_jobs → clean_job → enrich_job_with_skills → get_skill_counts
    """
    # Step 1: Load raw jobs from the selected source
    try:
        raw_jobs = load_raw_jobs_for_source(source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Sample data file not found at: {_SAMPLE_DATA_PATH}",
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    # Step 2: Clean each raw job (normalize text fields)
    cleaned_jobs = [clean_job(job) for job in raw_jobs]

    # Step 3: Enrich each cleaned job with extracted skills
    enriched_jobs = [enrich_job_with_skills(job) for job in cleaned_jobs]

    # Step 4: Count and sort skills across all jobs
    all_skill_counts = get_skill_counts(enriched_jobs)

    # Step 5: Slice to the requested top_n
    top_skills = all_skill_counts[:top_n]

    return {"skills": top_skills}
