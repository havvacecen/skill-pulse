"""
skills.py
---------
Defines the /skills endpoint for the SkillPulse API.

Purpose:
    Runs the full SkillPulse pipeline in memory and returns the top N
    most-demanded skills found across the sample job dataset.

Endpoint:
    GET /skills?top_n=10
    Response: {"skills": [{"skill": "python", "count": 8}, ...]}

Pipeline steps performed on each request:
    1. Load raw jobs from disk   (ingestion)
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

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /skills
# ---------------------------------------------------------------------------

@router.get("/skills")
def get_top_skills(
    top_n: int = Query(default=10, ge=1, le=100, description="Number of top skills to return"),
) -> dict:
    """
    Return the most frequently mentioned skills in the sample job dataset.

    Query parameters:
        top_n (int): How many skills to include in the response.
                     Must be between 1 and 100. Defaults to 10.

    Input:  query param ?top_n=<int>
    Output: {"skills": [{"skill": "python", "count": 8}, ...]}

    Pipeline executed on every call (no caching in Phase 1):
        load_jobs → clean_job → enrich_job_with_skills → get_skill_counts
    """
    # Step 1: Load raw jobs from the sample data file
    try:
        raw_jobs = load_jobs(str(_SAMPLE_DATA_PATH))
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Sample data file not found at: {_SAMPLE_DATA_PATH}",
        )

    # Step 2: Clean each raw job (normalize text fields)
    cleaned_jobs = [clean_job(job) for job in raw_jobs]

    # Step 3: Enrich each cleaned job with extracted skills
    enriched_jobs = [enrich_job_with_skills(job) for job in cleaned_jobs]

    # Step 4: Count and sort skills across all jobs
    all_skill_counts = get_skill_counts(enriched_jobs)

    # Step 5: Slice to the requested top_n
    top_skills = all_skill_counts[:top_n]

    return {"skills": top_skills}
