"""
test_cleaning.py
----------------
Tests for the cleaning pipeline logic.
Ensures text normalization works and job records are cleaned without mutation.
"""

import pytest
from src.core.pipeline.cleaning import normalize_text, clean_job


# ---------------------------------------------------------------------------
# normalize_text Tests
# ---------------------------------------------------------------------------

def test_normalize_text_basic():
    """Verify basic casing and whitespace cleaning."""
    assert normalize_text("  Senior  DATA Engineer  ") == "senior data engineer"
    assert normalize_text("Python\nSQL\tAirflow") == "python sql airflow"


def test_normalize_text_empty_and_null():
    """Verify safety with missing or empty values."""
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""
    assert normalize_text(None) == ""
    assert normalize_text(123) == ""  # Non-string input should return ""


# ---------------------------------------------------------------------------
# clean_job Tests
# ---------------------------------------------------------------------------

def test_clean_job_normalization():
    """Verify that all target text fields are normalized."""
    raw_job = {
        "title": "  SOFTWARE Engineer  ",
        "description": "  LOVES   Python  ",
        "location": "BERLIN ",
        "remote_type": "REMOTE",
        "source": "LINKEDIN",
        "seniority": "SENIOR",
        "employment_type": "FULL-TIME",
        "tags": ["ignored"]
    }
    
    cleaned = clean_job(raw_job)
    
    assert cleaned["title"] == "software engineer"
    assert cleaned["description"] == "loves python"
    assert cleaned["location"] == "berlin"
    assert cleaned["remote_type"] == "remote"
    assert cleaned["source"] == "linkedin"
    assert cleaned["seniority"] == "senior"
    assert cleaned["employment_type"] == "full-time"


def test_clean_job_passthrough():
    """Verify that pass-through fields are not changed."""
    raw_job = {
        "id": "job_123",
        "company": "Tech Corp",
        "source_url": "https://tech.corp/jobs/1",
        "posted_at": "2024-05-01",
        "tags": ["python", "sql"]
    }
    
    cleaned = clean_job(raw_job)
    
    assert cleaned["id"] == "job_123"
    assert cleaned["company"] == "Tech Corp"
    assert cleaned["source_url"] == "https://tech.corp/jobs/1"
    assert cleaned["posted_at"] == "2024-05-01"
    assert cleaned["tags"] == ["python", "sql"]


def test_clean_job_no_mutation():
    """Verify that the original dictionary is not modified."""
    raw_job = {"title": "Dirty TITLE"}
    
    clean_job(raw_job)
    
    # Original should still have the dirty title
    assert raw_job["title"] == "Dirty TITLE"


def test_clean_job_missing_keys():
    """Verify that missing keys return safe defaults instead of crashing."""
    raw_job = {} # Completely empty input
    
    cleaned = clean_job(raw_job)
    
    assert cleaned["title"] == ""
    assert cleaned["tags"] == []
    assert cleaned["id"] is None
