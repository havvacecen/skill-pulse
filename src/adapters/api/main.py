"""
main.py
-------
Entry point for the SkillPulse FastAPI application.

This file creates the FastAPI app instance and registers all route modules.
To run the server locally:
    uvicorn src.adapters.api.main:app --reload

Constraints:
    - No database
    - No authentication
    - No async endpoints
    - Beginner-readable, flat structure
"""

from fastapi import FastAPI

from src.adapters.api.routes import health, skills

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SkillPulse API",
    description="Serves top skill statistics derived from the SkillPulse pipeline.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

# Each router is defined in its own file under routes/
app.include_router(health.router)
app.include_router(skills.router)
