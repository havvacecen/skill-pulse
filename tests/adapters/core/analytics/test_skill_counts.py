"""
test_skill_counts.py
--------------------
Tests for the skill count aggregation logic.
Ensures skills are counted correctly and sorted by frequency.
"""

import pytest
from src.core.analytics.skill_counts import get_skill_counts


def test_get_skill_counts_basic():
    """Verify basic aggregation across multiple jobs."""
    jobs = [
        {"extracted_skills": ["python", "sql"]},
        {"extracted_skills": ["python", "airflow"]},
        {"extracted_skills": ["python"]}
    ]
    
    results = get_skill_counts(jobs)
    
    # We expect 3 skills in total: python, sql, airflow
    assert len(results) == 3
    
    # Python should be first with count 3
    assert results[0]["skill"] == "python"
    assert results[0]["count"] == 3


def test_get_skill_counts_sorting():
    """Verify that results are sorted descending by count."""
    jobs = [
        {"extracted_skills": ["sql"]},
        {"extracted_skills": ["python", "python", "python"]}, # multiple mentions in one job (if allowed by extraction)
        {"extracted_skills": ["python", "sql"]},
        {"extracted_skills": ["sql"]}
    ]
    # Counts: sql=3, python=4
    
    results = get_skill_counts(jobs)
    
    assert results[0]["skill"] == "python"
    assert results[0]["count"] == 4
    assert results[1]["skill"] == "sql"
    assert results[1]["count"] == 3


def test_get_skill_counts_empty():
    """Verify empty input returns empty results."""
    assert get_skill_counts([]) == []


def test_get_skill_counts_missing_keys():
    """Verify safety when jobs are missing the skills field."""
    jobs = [
        {"extracted_skills": ["python"]},
        {"id": "no-skills-here"},
        {"extracted_skills": None}
    ]
    
    results = get_skill_counts(jobs)
    
    assert len(results) == 1
    assert results[0]["skill"] == "python"
    assert results[0]["count"] == 1


def test_get_skill_counts_invalid_data():
    """Verify that non-list skill data is ignored safely."""
    jobs = [
        {"extracted_skills": "not-a-list"},
        {"extracted_skills": ["python"]}
    ]
    
    results = get_skill_counts(jobs)
    
    assert len(results) == 1
    assert results[0]["skill"] == "python"
    assert results[0]["count"] == 1
