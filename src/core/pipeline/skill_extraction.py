"""
skill_extraction.py
-------------------
Identifies technical skills mentioned in job postings using keyword matching.

This module works on cleaned job dictionaries. It searches for predefined
keywords in the job title and description to produce a list of found skills.
"""

from pathlib import Path


SKILLS_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "skills.yaml"


def load_skill_keywords(config_path: Path = SKILLS_CONFIG_PATH) -> list[str]:
    """
    Load skill keywords from configs/skills.yaml.

    Input:
        config_path (Path): Path to a simple YAML file with a 'skills:' list.

    Output:
        list[str]: Skill keywords in the same order as the config file.

    Core Logic:
        1. Read the config file line by line.
        2. Keep only list items written as '- skill_name'.
        3. Normalize each skill to lowercase for matching cleaned text.

    Edge Cases:
        - Empty lines and comments are ignored.
        - Missing config file raises FileNotFoundError.
    """
    skill_keywords = []

    with config_path.open("r", encoding="utf-8") as config_file:
        for line in config_file:
            clean_line = line.strip()

            if not clean_line or clean_line.startswith("#"):
                continue

            if clean_line.startswith("- "):
                skill = clean_line.removeprefix("- ").strip().lower()
                skill_keywords.append(skill)

    return skill_keywords


# Loaded from configs/skills.yaml so the skill list can change without editing code.
SKILL_KEYWORDS = load_skill_keywords()


def extract_skills_from_text(text: str) -> list[str]:
    """
    Search for known skill keywords within a string.

    Input:
        text (str): A normalized, lowercase string (e.g. "we need a python dev").

    Output:
        list[str]: A list of found skills (e.g. ["python"]).

    Core Logic:
        1. Loop through each skill in SKILL_KEYWORDS.
        2. Check if the skill string exists inside the text.
        3. If found, add it to the results list.

    Edge Cases:
        - Text is empty or None: Returns an empty list.
        - No skills found: Returns an empty list.
        - Multiple skills found: Returns all of them.
    """
    if not text:
        return []

    found_skills = []
    
    for skill in SKILL_KEYWORDS:
        # Simple containment check. 
        # Note: In the future, we might use regex for better word-boundary matching.
        if skill in text:
            found_skills.append(skill)
            
    return found_skills


def enrich_job_with_skills(job: dict) -> dict:
    """
    Add an 'extracted_skills' field to a job dictionary.

    Input:
        job (dict): A cleaned job dictionary from cleaning.py.

    Output:
        dict: A new dictionary containing all original fields plus 'extracted_skills'.

    Core Logic:
        1. Combine the title and description into one searchable string.
        2. Use extract_skills_from_text to find keywords.
        3. Return a copy of the job dict with the new data.

    Edge Cases:
        - Title or description missing: Handled safely by extract_skills_from_text.
        - Job dictionary is empty: Returns a dict with only 'extracted_skills': [].
    """
    # Get text from title and description (default to empty string if missing)
    title = job.get("title", "")
    description = job.get("description", "")
    
    # Combine them to search both at once
    combined_text = f"{title} {description}"
    
    # Extract the skills
    extracted = extract_skills_from_text(combined_text)
    
    # Create a new dictionary (no mutation)
    enriched_job = job.copy()
    enriched_job["extracted_skills"] = extracted
    
    return enriched_job
