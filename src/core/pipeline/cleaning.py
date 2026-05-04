"""
cleaning.py
-----------
Takes raw job dictionaries straight from ingestion and returns clean,
consistent job dictionaries ready for the next pipeline step.

This module does NOT extract skills, does NOT touch the database,
and does NOT mutate any input data.
"""

import re


# ---------------------------------------------------------------------------
# normalize_text
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Clean a single text value so all text fields are consistent.

    Input:
        text (str): Any raw string value, e.g. "  Senior  Python  Dev  "
                    Can also be None or a non-string — handled safely.

    Output:
        str: A cleaned string, e.g. "senior python dev"
             Returns "" (empty string) if the input is None or not a string.

    Core logic:
        1. Return "" immediately for None or non-string values.
        2. Lowercase everything  →  "Senior Dev" becomes "senior dev"
        3. Strip leading/trailing spaces  →  "  hello  " becomes "hello"
        4. Collapse repeated whitespace  →  "hello   world" becomes "hello world"
           (re.sub replaces any run of whitespace characters with a single space)

    Edge cases:
        - None input           → returns ""  (no crash)
        - Integer/float input  → returns ""  (no crash)
        - Empty string ""      → returns ""
        - Only spaces "   "    → returns ""
        - Tabs or newlines     → collapsed into a single space, then stripped
    """
    # Guard: if the value is missing or not a string, return empty string
    if not isinstance(text, str):
        return ""

    # Step 1: lowercase
    text = text.lower()

    # Step 2: strip outer whitespace
    text = text.strip()

    # Step 3: collapse any run of whitespace (spaces, tabs, newlines) to one space
    text = re.sub(r"\s+", " ", text)

    return text


# ---------------------------------------------------------------------------
# clean_job
# ---------------------------------------------------------------------------

def clean_job(raw_job: dict) -> dict:
    """
    Produce a cleaned copy of a single raw job dictionary.

    Input:
        raw_job (dict): One raw job record from ingestion, e.g.:
            {
                "id": "abc123",
                "title": "  Senior  Data Engineer  ",
                "description": "We use Python, SQL, Airflow.",
                "location": "ISTANBUL",
                "remote_type": "Remote",
                "source": "LinkedIn",
                "seniority": "senior",
                "company": "Acme Corp",
                "source_url": "https://...",
                "posted_at": "2024-01-15",
                "employment_type": "full-time",
                "tags": ["python", "sql"]
            }

    Output:
        dict: A new dictionary with the same keys. Text fields are normalized;
              pass-through fields are copied exactly as-is.
              The original raw_job dict is NEVER modified.

    Core logic:
        - Text fields (title, description, location, remote_type, source,
          seniority, employment_type) are passed through normalize_text().
        - Pass-through fields (id, company, source_url, posted_at,
          tags) are copied without any change.
        - Missing keys are handled safely:
            - Missing text field  → defaults to ""
            - Missing tags        → defaults to []

    Edge cases:
        - Key is missing in raw_job    → safe default, no KeyError
        - Text field is None           → normalize_text returns ""
        - tags is None                 → replaced with []
        - raw_job is empty dict {}     → returns a dict of all safe defaults
    """
    # --- Text fields: normalize case and whitespace ---

    title = normalize_text(raw_job.get("title"))
    description = normalize_text(raw_job.get("description"))
    location = normalize_text(raw_job.get("location"))
    remote_type = normalize_text(raw_job.get("remote_type"))
    source = normalize_text(raw_job.get("source"))
    seniority = normalize_text(raw_job.get("seniority"))
    employment_type = normalize_text(raw_job.get("employment_type"))

    # --- Pass-through fields: copy exactly as-is ---

    job_id = raw_job.get("id")                          # unique identifier
    company = raw_job.get("company")                    # company name (kept as-is)
    source_url = raw_job.get("source_url")              # original job posting URL
    posted_at = raw_job.get("posted_at")                # date string or None

    # tags is a list; if missing or None, use an empty list as the safe default
    tags = raw_job.get("tags") or []

    # --- Build and return a brand-new dict (no mutation of raw_job) ---

    return {
        "id":              job_id,
        "title":           title,
        "description":     description,
        "location":        location,
        "remote_type":     remote_type,
        "source":          source,
        "seniority":       seniority,
        "company":         company,
        "source_url":      source_url,
        "posted_at":       posted_at,
        "employment_type": employment_type,
        "tags":            tags,
    }
