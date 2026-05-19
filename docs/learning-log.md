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


---

## 2026-05-04

Today I worked on:
- `src/core/pipeline/cleaning.py` — normalization layer (lowercase, strip, collapse whitespace)
- `src/core/pipeline/skill_extraction.py` — keyword-based enrichment (python, sql, airflow, etc.)
- `src/core/analytics/skill_counts.py` — aggregation layer (frequency counting & sorting)
- `tests/adapters/core/` — full test coverage for all three new modules
- `.gitignore` — added IDE and build artifact exclusions

What it does:
- `cleaning.py`: transforms messy raw strings into consistent lowercase text.
- `skill_extraction.py`: identifies technical keywords in titles and descriptions.
- `skill_counts.py`: calculates which skills are most in-demand across the dataset.

Input:
- `list[dict]` (raw job records from ingestion)

Output:
- `list[dict]` (enriched job records with `extracted_skills` key)
- `list[dict]` (sorted skill frequency statistics)

Interview explanation:
- I implemented a "pure function" approach where each transformation step returns a brand-new object instead of mutating the input. This prevents bugs where one part of the pipeline accidentally changes data for another part.
- The separation of cleaning from extraction ensures that keywords are always matched against a predictable, normalized format.
- I used simple string containment for extraction to keep the logic lightweight and readable before moving to more complex NLP methods.


---

## 2026-05-19

Today I worked on:
- `src/adapters/api/__init__.py` — package marker for the API adapter
- `src/adapters/api/main.py` — FastAPI app instance; registers all routers
- `src/adapters/api/routes/__init__.py` — package marker for the routes sub-package
- `src/adapters/api/routes/health.py` — `GET /health` endpoint
- `src/adapters/api/routes/skills.py` — `GET /skills` endpoint
- `tests/adapters/api/test_health.py` — 2 tests for the health endpoint
- `tests/adapters/api/test_skills.py` — 8 tests for the skills endpoint
- `requirements.txt` — activated `fastapi`, `uvicorn[standard]`, `httpx`

What each piece does:
- `main.py`: Creates the FastAPI `app` object and wires up the two routers. This is the single entry point uvicorn points at.
- `health.py`: Returns `{"status": "ok"}` with no I/O. Used to confirm the server is alive.
- `skills.py`: Runs the full pipeline on every request — load → clean → extract → count — and returns the top N skills as JSON. Path to the data file is resolved relative to the project root using `Path(__file__).parents[5]` so it works regardless of where uvicorn is started.

Input:
- `GET /health` — no parameters
- `GET /skills?top_n=<int>` — optional `top_n` query param (1–100, default 10)

Output:
- `/health` → `{"status": "ok"}`
- `/skills` → `{"skills": [{"skill": "python", "count": 8}, ...]}`

Edge cases handled:
- `top_n < 1` or `top_n > 100` → FastAPI returns HTTP 422 automatically (via `Query(ge=1, le=100)`)
- Sample data file missing → HTTP 500 with a descriptive message
- Jobs with no extracted skills → handled safely by downstream modules

Test result:
- `10 passed` ✅ (2 health + 8 skills)

Interview explanation:
- I separated the app wiring (`main.py`) from the endpoint logic (`routes/`) so each concern lives in its own file. Adding a new endpoint means creating a new file and one `include_router()` line — nothing else changes.
- The `/skills` endpoint deliberately re-runs the pipeline on every call. There is no caching in Phase 1; this keeps the code simple and transparent. Caching would be a Phase 2 optimization once the data source grows.
- Using FastAPI's `Query(ge=1, le=100)` means the framework validates the input and returns a standard 422 error automatically — I didn't have to write any manual validation code.
