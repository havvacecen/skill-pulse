## File Instruction 

## Date: xx.xx.xxxx

Today I worked on:
- sample_file_extractor.py

What it does:
- Reads sample job data from JSON.

Input:
- data/samples/sample_jobs.json

Output:
- list[dict] raw job records

Interview explanation:
- I separated ingestion from transformation so each source can have its own extractor.

---

## 2026-05-03

Today I worked on:
- `README.md` — lean project structure with folder responsibilities
- `data/raw/sample_jobs.json` — 12 synthetic job records (4 roles, realistic fields)
- `src/adapters/ingestion/ingestion.py` — minimal function to load raw JSON into memory
- `tests/adapters/ingestion/test_ingestion.py` — 6 tests covering happy path and edge cases
- `requirements.txt` — added pytest as the only Phase 1 dependency
- `conftest.py` — empty file in project root so pytest can resolve `src/` imports

What each piece does:
- `README.md`: documents the folder tree and one-sentence responsibility per folder; serves as the project map.
- `sample_jobs.json`: provides realistic synthetic data so the pipeline can be tested without a real scraper.
- `ingestion.py`: opens a JSON file, validates it is a list, and returns it as `list[dict]`. No transformation here.
- `test_ingestion.py`: verifies the happy path (valid file, correct keys, real file loads) and all three failure modes.

Input:
- `data/raw/sample_jobs.json` — a JSON array of raw job records

Output:
- `list[dict]` — one dictionary per job, exactly as stored in the file

Edge cases handled:
- File does not exist → `FileNotFoundError`
- File is not valid JSON → `json.JSONDecodeError`
- JSON root is not a list (e.g. a dict) → `ValueError`

Test result:
- `6 passed in 0.09s` ✅

Interview explanation:
- The ingestion step is the entry point of the pipeline. Its only job is to load raw data — no cleaning, no transformation. This separation means I can swap the source (file today, API later) without touching anything downstream.
- I used `pathlib.Path` instead of raw strings because it handles cross-platform path differences cleanly.

