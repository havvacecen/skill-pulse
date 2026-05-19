"""
health.py
---------
Defines the /health endpoint for the SkillPulse API.

Purpose:
    Lets callers verify that the server is running and reachable.
    Returns a simple JSON object with a status field.

Endpoint:
    GET /health
    Response: {"status": "ok"}

Constraints:
    - No database calls
    - No external I/O
    - Synchronous (no async)
"""

from fastapi import APIRouter

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

# APIRouter groups related endpoints. It is registered in main.py.
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@router.get("/health")
def health_check() -> dict:
    """
    Health-check endpoint.

    Returns a fixed JSON response to confirm the API is up and running.

    Input:  none
    Output: {"status": "ok"}
    """
    return {"status": "ok"}
