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
    selected_remote_type: str,
    selected_seniority: str,
    selected_dates: tuple[date, date],
) -> list[dict]:
    """Apply simple dashboard filters to the processed jobs."""
    filtered_jobs = []

    for job in jobs:
        posted_date = parse_posted_date(job)

        role_matches = selected_role == "All roles" or job.get("title") == selected_role
        source_matches = selected_source == "Sample data"
        remote_type_matches = (
            selected_remote_type == "All work types"
            or job.get("remote_type") == selected_remote_type
        )
        seniority_matches = (
            selected_seniority == "All seniority levels"
            or job.get("seniority") == selected_seniority
        )
        date_matches = posted_date is None or selected_dates[0] <= posted_date <= selected_dates[1]

        if (
            role_matches
            and source_matches
            and remote_type_matches
            and seniority_matches
            and date_matches
        ):
            filtered_jobs.append(job)

    return filtered_jobs


def calculate_remote_ratio(jobs: list[dict]) -> float:
    """Calculate the percentage of filtered jobs marked as remote."""
    if not jobs:
        return 0.0

    remote_jobs = [job for job in jobs if job.get("remote_type") == "remote"]
    return (len(remote_jobs) / len(jobs)) * 100


st.set_page_config(page_title="SkillPulse Dashboard", layout="wide")

st.title("SkillPulse Dashboard")
st.write(
    "A minimal dashboard that shows which technical skills appear most often "
    "in the current sample job dataset."
)

jobs = load_processed_jobs()

roles = ["All roles"] + sorted({job["title"] for job in jobs if job.get("title")})
sources = ["Sample data"]
remote_types = ["All work types"] + sorted(
    {job["remote_type"] for job in jobs if job.get("remote_type")}
)
seniority_levels = ["All seniority levels"] + sorted(
    {job["seniority"] for job in jobs if job.get("seniority")}
)
posted_dates = [parse_posted_date(job) for job in jobs]
posted_dates = [posted_date for posted_date in posted_dates if posted_date is not None]

min_date = min(posted_dates)
max_date = max(posted_dates)

selected_role = st.selectbox("Role", roles)
selected_source = st.selectbox("Source", sources)
selected_remote_type = st.selectbox("Remote / Hybrid / Onsite", remote_types)
selected_seniority = st.selectbox("Seniority", seniority_levels)
top_n = st.slider("Top skills to show", min_value=3, max_value=10, value=5)
selected_dates = st.date_input(
    "Posted date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(selected_dates) != 2:
    st.info("Select a start and end date to see filtered skill counts.")
else:
    filtered_jobs = filter_jobs(
        jobs,
        selected_role,
        selected_source,
        selected_remote_type,
        selected_seniority,
        selected_dates,
    )
    skill_counts = get_skill_counts(filtered_jobs)
    top_skill_counts = skill_counts[:top_n]
    unique_skill_count = len(skill_counts)
    remote_ratio = calculate_remote_ratio(filtered_jobs)

    total_jobs_column, unique_skills_column, remote_ratio_column = st.columns(3)
    total_jobs_column.metric("Total jobs", len(filtered_jobs))
    unique_skills_column.metric("Unique skills", unique_skill_count)
    remote_ratio_column.metric("Remote ratio", f"{remote_ratio:.0f}%")

    st.subheader("Top Skills")
    st.caption(f"Showing top {min(top_n, len(skill_counts))} skills from {len(filtered_jobs)} job postings.")

    if top_skill_counts:
        st.dataframe(top_skill_counts, use_container_width=True, hide_index=True)
        st.bar_chart(top_skill_counts, x="skill", y="count")
    else:
        st.warning("No skills found for the selected filters.")
