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
- `src/adapters/api/__init__.py` - package marker for the API adapter
- `src/adapters/api/main.py` - FastAPI app entry point
- `src/adapters/api/routes/__init__.py` - package marker for API routes
- `src/adapters/api/routes/health.py` - health-check route
- `src/adapters/api/routes/skills.py` - skills route that runs the pipeline and returns skill counts
- `tests/adapters/api/__init__.py` - package marker for API tests
- `tests/adapters/api/test_health.py` - tests for `GET /health`
- `tests/adapters/api/test_skills.py` - tests for `GET /skills`
- `requirements.txt` - API and test dependencies: `pytest`, `fastapi`, `uvicorn[standard]`, and `httpx`

What each piece does:
- `main.py`: Creates the FastAPI `app` object and registers the health and skills routers.
- `health.py`: Defines `GET /health`, a simple endpoint that returns `{"status": "ok"}` with no file access or pipeline work.
- `skills.py`: Defines `GET /skills`, loads sample jobs, cleans them, extracts skills, counts them, sorts them, and returns the top results.
- `test_health.py`: Checks that `/health` returns HTTP 200 and the expected JSON body.
- `test_skills.py`: Checks that `/skills` returns HTTP 200, includes a `skills` key, returns items with `skill` and `count`, respects `top_n`, rejects invalid `top_n` values, and sorts counts from highest to lowest.

API endpoints:
- `GET /health` - no query parameters
- `GET /skills` - optional `top_n` query parameter, default `10`
- `GET /skills?top_n=3` - returns at most 3 skill results

Input:
- `/health` - no input
- `/skills` - optional `top_n` integer from 1 to 100
- `data/raw/sample_jobs.json` - sample job records used by the skills endpoint

Output:
- `/health` -> `{"status": "ok"}`
- `/skills` -> `{"skills": [{"skill": "python", "count": 8}, ...]}`

Edge cases handled:
- `top_n=0` -> HTTP 422 from FastAPI validation
- `top_n=101` -> HTTP 422 from FastAPI validation
- Missing sample data file -> HTTP 500 with a clear error message

Debugging/recovery work:
- The first focused API test run showed that `/health` passed, but `/skills` returned HTTP 500.
- The error message showed that the API was looking for `data/raw/sample_jobs.json` one folder above the real project root.
- Root cause: `_PROJECT_ROOT` in `skills.py` used `Path(__file__).resolve().parents[5]`, which resolved to `SkillPulse_Project` instead of `skill-pulse`.
- Smallest safe patch: changed it to `parents[4]`, so the API resolves the data path to the actual repository root.

Test result:
- `.\.venv\Scripts\python.exe -m pytest tests/adapters/api`
- `10 passed in 0.25s`

Interview explanation:
- I built the API as a thin adapter around the existing pipeline. FastAPI handles HTTP requests, but the core logic still lives in ingestion, cleaning, extraction, and analytics modules.
- The `/health` endpoint is intentionally simple because it only proves that the API process is running.
- The `/skills` endpoint reuses the existing pipeline instead of duplicating business logic inside the route.
- `Query(ge=1, le=100)` keeps validation beginner-readable and lets FastAPI return standard 422 errors automatically.
- The recovery work was a path-resolution bug, not a pipeline bug. The endpoint failed because it could not find the sample data file, so the safest fix was to correct the project-root calculation only.


---

## 2026-05-20

Today I worked on:
- `dashboard/app.py` - first minimal Streamlit dashboard entry point
- `requirements.txt` - enabled the `streamlit` dependency for the dashboard phase

What each piece does:
- `app.py`: Creates a simple Streamlit page titled `SkillPulse Dashboard`.
-           Loads the current sample job data from `data/raw/sample_jobs.json`.
-           Reuses the existing pipeline functions: `load_jobs`, `clean_job`, `enrich_job_with_skills`, and `get_skill_counts`.
-           Shows the top extracted skills as a table and a bar chart.
-           Adds simple filters for role, source, and posted date range.
- `requirements.txt`: Activates Streamlit so the dashboard can be run locally.

Dashboard functionality:
- Page title: `SkillPulse Dashboard`
- Short project description explaining that the dashboard shows skills from the sample job dataset
- Role filter based on job titles in the sample data
- Source filter limited to `Sample data`, because Phase 1 does not use real LinkedIn, Kariyer.net, RemoteOK, or Wellfound data yet
- Posted date range filter based on the `posted_at` field
- Top skills table
- Top skills bar chart
- Empty-state message when the selected filters return no skills

API/dashboard integration work:
- No API code was changed.
- The dashboard reuses the same pipeline logic that powers the `/skills` API endpoint.
- This keeps the dashboard and API consistent without adding database logic or duplicating skill-counting logic.

Input:
- `data/raw/sample_jobs.json` - the current Phase 1 sample/mock job dataset
- Streamlit filter selections: role, source, and posted date range

Output:
- A Streamlit dashboard page showing filtered top skill counts
- A table of records like `{"skill": "python", "count": 12}`
- A bar chart using the same skill count results

Test result:
- `.\.venv\Scripts\python.exe -m py_compile dashboard\app.py`
- passed
- `.\.venv\Scripts\python.exe -m pytest`
- `34 passed in 0.32s`

How to run locally:
- `.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py`

Interview explanation:
- I added the first dashboard as a thin presentation layer over the existing pipeline. The dashboard does not clean data, extract skills, or count skills by itself; it calls the modules that already do those jobs.
- This keeps the project modular: ingestion, cleaning, extraction, analytics, API, and dashboard each have their own responsibility.
- I kept the source filter honest for Phase 1 by showing only `Sample data`. Even though the mock records contain source-like values, the product should not present them as real integrations before real ingestion exists.
- Streamlit is useful here because it gives a quick product view of the pipeline output without adding frontend complexity.
