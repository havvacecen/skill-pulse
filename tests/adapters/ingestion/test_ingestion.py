"""
test_ingestion.py
-----------------
Tests for src/adapters/ingestion/ingestion.py

Run with:
    pytest tests/adapters/ingestion/test_ingestion.py -v
"""

import json
import pytest
from pathlib import Path

# We import the function we want to test
from src.adapters.ingestion.ingestion import load_jobs


# ── Helpers ──────────────────────────────────────────────────────────────────

def write_json(tmp_path: Path, content) -> Path:
    """Write any content as JSON to a temp file and return its path."""
    file = tmp_path / "jobs.json"
    file.write_text(json.dumps(content), encoding="utf-8")
    return file


# ── Happy path ────────────────────────────────────────────────────────────────

def test_returns_list_of_dicts(tmp_path):
    """load_jobs should return a list when given a valid JSON array file."""
    fake_jobs = [
        {"id": "job_001", "title": "Data Engineer"},
        {"id": "job_002", "title": "Backend Engineer"},
    ]
    file = write_json(tmp_path, fake_jobs)

    result = load_jobs(str(file))

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["title"] == "Data Engineer"


def test_returns_correct_keys(tmp_path):
    """Each dict in the result should contain the expected keys."""
    fake_jobs = [
        {
            "id": "job_001",
            "title": "Data Engineer",
            "company": "TestCo",
            "tags": ["Python", "SQL"],
        }
    ]
    file = write_json(tmp_path, fake_jobs)

    result = load_jobs(str(file))

    assert "id" in result[0]
    assert "title" in result[0]
    assert "tags" in result[0]


def test_loads_real_sample_file():
    """load_jobs should successfully read the real sample_jobs.json file."""
    result = load_jobs("data/raw/sample_jobs.json")

    assert isinstance(result, list)
    assert len(result) > 0          # at least one record
    assert "title" in result[0]     # first record has a title field


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_raises_file_not_found():
    """load_jobs should raise FileNotFoundError when the file does not exist."""
    with pytest.raises(FileNotFoundError):
        load_jobs("data/raw/does_not_exist.json")


def test_raises_value_error_when_not_a_list(tmp_path):
    """load_jobs should raise ValueError when the JSON root is not a list."""
    file = write_json(tmp_path, {"key": "value"})  # JSON object, not array

    with pytest.raises(ValueError):
        load_jobs(str(file))


def test_raises_json_decode_error_on_invalid_json(tmp_path):
    """load_jobs should raise json.JSONDecodeError when the file is not valid JSON."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("this is not json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_jobs(str(bad_file))
