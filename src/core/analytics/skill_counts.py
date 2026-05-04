"""
skill_counts.py
---------------
Provides analytics on extracted skills across multiple job records.

This module takes a list of jobs (already processed by skill_extraction.py)
and aggregates the skills to see which are most common.
"""

def get_skill_counts(jobs: list[dict]) -> list[dict]:
    """
    Count the frequency of each skill across a collection of jobs.

    Input:
        jobs (list[dict]): A list of enriched job dictionaries, 
                           each containing an 'extracted_skills' list.

    Output:
        list[dict]: A sorted list of skill counts, for example:
                    [
                        {"skill": "python", "count": 10},
                        {"skill": "sql", "count": 8}
                    ]

    Core Logic:
        1. Initialize an empty dictionary for counts.
        2. Loop through every job record.
        3. Extract the 'extracted_skills' list (handle missing with []).
        4. Loop through each skill in that list and increment the count.
        5. Convert the counts dictionary into a list of dictionaries.
        6. Sort the list by 'count' in descending order.

    Edge Cases:
        - Input list is empty: Returns an empty list [].
        - Jobs have no skills: Returns an empty list [].
        - 'extracted_skills' key is missing: Handled safely, count remains 0.
        - Not a list in 'extracted_skills': Handled safely by defaulting to empty list.
    """
    counts = {}

    # Step 1: Aggregate the counts
    for job in jobs:
        # Get the skills list safely. 
        # We check if it's actually a list to avoid errors with bad data.
        skills = job.get("extracted_skills", [])
        if not isinstance(skills, list):
            skills = []

        for skill in skills:
            if skill in counts:
                counts[skill] += 1
            else:
                counts[skill] = 1

    # Step 2: Convert to list of dictionaries
    # Before: {"python": 3, "sql": 1}
    # After: [{"skill": "python", "count": 3}, {"skill": "sql", "count": 1}]
    results = []
    for skill_name, count_value in counts.items():
        results.append({
            "skill": skill_name,
            "count": count_value
        })

    # Step 3: Sort by count descending (highest first)
    # The lambda tells Python to sort based on the "count" key of each dict.
    results.sort(key=lambda x: x["count"], reverse=True)

    return results
