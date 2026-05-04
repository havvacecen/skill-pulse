"""
test_skill_extraction.py
------------------------
Tests for the skill extraction logic.
Ensures keywords are found in job fields and output is consistent.
"""

import pytest
from src.core.pipeline.skill_extraction import extract_skills_from_text, enrich_job_with_skills


# ---------------------------------------------------------------------------
# extract_skills_from_text Tests
# ---------------------------------------------------------------------------

def test_extract_skills_multiple():
    """Verify multiple skills are found in a single string."""
    text = "we are looking for a python developer with sql and spark experience."
    found = extract_skills_from_text(text)
    
    assert "python" in found
    assert "sql" in found
    assert "spark" in found
    assert len(found) == 3


def test_extract_skills_none_found():
    """Verify empty list is returned when no keywords match."""
    text = "we need a chef who can cook pasta."
    assert extract_skills_from_text(text) == []


def test_extract_skills_empty_input():
    """Verify safety with empty or None strings."""
    assert extract_skills_from_text("") == []
    assert extract_skills_from_text(None) == []


# ---------------------------------------------------------------------------
# enrich_job_with_skills Tests
# ---------------------------------------------------------------------------

def test_enrich_job_searches_both_fields():
    """Verify skills are pulled from both title and description."""
    job = {
        "title": "python lead",
        "description": "must know snowflake and dbt",
        "location": "remote"
    }
    
    enriched = enrich_job_with_skills(job)
    skills = enriched["extracted_skills"]
    
    assert "python" in skills
    assert "snowflake" in skills
    assert "dbt" in skills
    assert len(skills) == 3


def test_enrich_job_preserves_original_fields():
    """Verify that original data (id, location, etc.) is still there."""
    job = {
        "id": "123",
        "title": "data engineer",
        "location": "london",
        "company": "data co"
    }
    
    enriched = enrich_job_with_skills(job)
    
    assert enriched["id"] == "123"
    assert enriched["location"] == "london"
    assert enriched["company"] == "data co"
    assert "extracted_skills" in enriched


def test_enrich_job_no_mutation():
    """Verify the original job dictionary is not modified."""
    job = {"title": "python dev"}
    
    enrich_job_with_skills(job)
    
    # Original should NOT have the extracted_skills key
    assert "extracted_skills" not in job


def test_enrich_job_missing_keys():
    """Verify safety when title or description is missing from dict."""
    job = {"location": "remote"} # Missing title and description
    
    enriched = enrich_job_with_skills(job)
    
    assert enriched["extracted_skills"] == []
    assert enriched["location"] == "remote"
