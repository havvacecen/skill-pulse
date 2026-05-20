"""
Minimal Streamlit dashboard for SkillPulse.

This app reuses the existing in-memory pipeline:
load sample jobs -> clean jobs -> extract skills -> count top skills.

Run locally:
    streamlit run dashboard/app.py
"""

from datetime import date
from pathlib import Path

import streamlit as st

from src.adapters.ingestion.ingestion import load_jobs
from src.core.analytics.skill_counts import get_skill_counts
from src.core.pipeline.cleaning import clean_job
from src.core.pipeline.skill_extraction import enrich_job_with_skills


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "sample_jobs.json"


def load_processed_jobs() -> list[dict]:
    """Load sample jobs and run the existing cleaning + skill extraction steps."""
    raw_jobs = load_jobs(str(SAMPLE_DATA_PATH))
    cleaned_jobs = [clean_job(job) for job in raw_jobs]
    return [enrich_job_with_skills(job) for job in cleaned_jobs]


def parse_posted_date(job: dict) -> date | None:
    """Convert a job's posted_at value to a date when possible."""
    posted_at = job.get("posted_at")
    if not posted_at:
        return None

    try:
        return date.fromisoformat(posted_at)
    except ValueError:
        return None


def filter_jobs(
    jobs: list[dict],
    selected_role: str,
    selected_source: str,
    selected_dates: tuple[date, date],
) -> list[dict]:
    """Apply simple dashboard filters to the processed jobs."""
    filtered_jobs = []

    for job in jobs:
        posted_date = parse_posted_date(job)

        role_matches = selected_role == "All roles" or job.get("title") == selected_role
        source_matches = selected_source == "Sample data"
        date_matches = posted_date is None or selected_dates[0] <= posted_date <= selected_dates[1]

        if role_matches and source_matches and date_matches:
            filtered_jobs.append(job)

    return filtered_jobs


st.set_page_config(page_title="SkillPulse Dashboard", layout="wide")

st.title("SkillPulse Dashboard")
st.write(
    "A minimal dashboard that shows which technical skills appear most often "
    "in the current sample job dataset."
)

jobs = load_processed_jobs()

roles = ["All roles"] + sorted({job["title"] for job in jobs if job.get("title")})
sources = ["Sample data"]
posted_dates = [parse_posted_date(job) for job in jobs]
posted_dates = [posted_date for posted_date in posted_dates if posted_date is not None]

min_date = min(posted_dates)
max_date = max(posted_dates)

selected_role = st.selectbox("Role", roles)
selected_source = st.selectbox("Source", sources)
selected_dates = st.date_input(
    "Posted date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(selected_dates) != 2:
    st.info("Select a start and end date to see filtered skill counts.")
else:
    filtered_jobs = filter_jobs(jobs, selected_role, selected_source, selected_dates)
    skill_counts = get_skill_counts(filtered_jobs)

    st.subheader("Top Skills")
    st.caption(f"Showing results from {len(filtered_jobs)} job postings.")

    if skill_counts:
        st.dataframe(skill_counts, use_container_width=True, hide_index=True)
        st.bar_chart(skill_counts, x="skill", y="count")
    else:
        st.warning("No skills found for the selected filters.")
