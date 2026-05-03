"""
ingestion.py
------------
Reads raw job data from a local JSON file and returns it as a list of dicts.

This is the ingestion step of the SkillPulse pipeline.
It does NOT clean or transform data — it only loads raw records into memory.
Extraction (parsing fields, enriching records) happens in a later step.
"""

import json
from pathlib import Path


def load_jobs(file_path: str) -> list[dict]:
    """
    Read a JSON file containing job records and return them as a list.

    Input:
        file_path (str): Path to the JSON file, e.g. "data/raw/sample_jobs.json"

    Output:
        list[dict]: A list of raw job dictionaries, one per job record.

    Edge cases:
        - File does not exist      → raises FileNotFoundError with a clear message
        - File is not valid JSON   → raises json.JSONDecodeError (from json.load)
        - JSON is not a list       → raises ValueError with a clear message
    """
    path = Path(file_path)

    # Edge case: file does not exist
    if not path.exists():
        raise FileNotFoundError(f"Job data file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)  # raises json.JSONDecodeError if file is not valid JSON

    # Edge case: JSON content is not a list (e.g. it's a dict or null)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array, got {type(data).__name__}")

    return data
