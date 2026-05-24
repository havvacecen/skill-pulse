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


---

## 2026-05-23

Today I worked on:
- `configs/skills.yaml` - new configuration file for skill keywords
- `src/core/pipeline/skill_extraction.py` - refactored skill extraction to load keywords from config
- `tests/adapters/core/pipeline/test_skill_extraction.py` - added coverage for loading skill keywords from config
- `dashboard/app.py` - polished the Streamlit dashboard with more filters, metrics, and a Top-N slider
- `README.md` - updated the project documentation to match the current implementation
- `src/adapters/ingestion/remoteok.py` - added a minimal RemoteOK ingestion adapter
- `tests/adapters/ingestion/test_remoteok.py` - added tests for RemoteOK mapping and request failure behavior

What each piece does:
- `skills.yaml`: Stores the tracked skill keywords outside Python code, including `python`, `sql`, `airflow`, `spark`, `kafka`, `aws`, `docker`, `dbt`, `snowflake`, and `pandas`.
- `skill_extraction.py`: Loads skill keywords from `configs/skills.yaml`, then keeps the same simple keyword matching behavior against cleaned title and description text.
- `test_skill_extraction.py`: Verifies that a simple YAML-style skill config is loaded in order and normalized to lowercase.
- `dashboard/app.py`: Still reuses `load_jobs`, `clean_job`, `enrich_job_with_skills`, and `get_skill_counts`, but now adds a Top-N slider, Remote / Hybrid / Onsite filter, Seniority filter, and summary metric cards.
- `README.md`: Explains the current architecture flow, project structure, pipeline stages, local setup commands, API endpoints, dashboard behavior, and current data strategy.
- `remoteok.py`: Fetches jobs from the public RemoteOK API and maps them into the same raw job dictionary shape used by `sample_jobs.json`.
- `test_remoteok.py`: Tests RemoteOK normalization and fetch behavior without making live network calls.

Input:
- `configs/skills.yaml` - a small YAML-style list of skill keywords used by skill extraction
- `data/raw/sample_jobs.json` - still used by the existing local sample pipeline, API, and dashboard
- `https://remoteok.com/api` - optional real RemoteOK source used by the new ingestion adapter
- Streamlit filter selections: role, source, remote type, seniority, posted date range, and Top-N count

Output:
- `list[str]` skill keywords loaded from configuration
- `list[dict]` enriched job records with `extracted_skills`
- `list[dict]` top skill count records such as `{"skill": "python", "count": 12}`
- `list[dict]` RemoteOK jobs normalized to the raw SkillPulse shape:
  `id`, `title`, `company`, `description`, `location`, `remote_type`, `source`, `source_url`, `posted_at`, `employment_type`, `seniority`, `tags`
- A Streamlit dashboard with filters, metric cards, top skills table, and bar chart
- README documentation that reflects the current implemented project state

Architecture changes:
- Skill extraction is now configuration-driven: changing tracked skills can happen in `configs/skills.yaml` instead of editing Python code.
- Ingestion now has two source paths:
  - local sample ingestion through `load_jobs`
  - RemoteOK ingestion through `fetch_remoteok_jobs`
- The API and dashboard still reuse the existing pipeline and were not changed to call RemoteOK directly.
- No database, Kafka, Spark, Airflow, Redis, or orchestration logic was added.

Dashboard functionality:
- Top-N slider controls how many skill rows appear in the table and chart.
- Remote / Hybrid / Onsite filter uses the existing `remote_type` field.
- Seniority filter is built dynamically from available job data.
- Metric cards show total filtered jobs, unique skills, and remote ratio.
- Empty states are still handled safely when date range or filters return no skill results.

RemoteOK ingestion mapping:
- `position` or `title` -> `title`
- `company` -> `company`
- `description` -> `description`
- `location` -> `location`, with `"Remote"` as a fallback
- `url` -> `source_url`
- `date`, `epoch`, or `date_epoch` -> `posted_at`
- `tags` -> `tags`
- `source` is always set to `"remoteok"`
- `remote_type` is always set to `"remote"`
- `seniority` is lightly inferred from the title using simple words like `junior`, `entry`, `senior`, `sr.`, and `lead`

Edge cases handled:
- Empty skill extraction input still returns an empty list.
- Missing or commented lines in `skills.yaml` are ignored by the loader.
- Missing RemoteOK fields fall back to safe defaults where possible.
- RemoteOK metadata rows are skipped.
- RemoteOK network and HTTP errors are wrapped in a clear `RuntimeError`.
- RemoteOK tests use fake clients, so the test suite does not depend on the live API.
- Dashboard remote ratio returns `0%` safely when no jobs match the filters.

Test result:
- `.\.venv\Scripts\python.exe -m pytest tests/adapters/core/pipeline/test_skill_extraction.py`
- `8 passed`
- `.\.venv\Scripts\python.exe -m pytest tests/adapters/ingestion`
- `9 passed`
- `.\.venv\Scripts\python.exe -m py_compile dashboard\app.py`
- passed
- `.\.venv\Scripts\python.exe -m pytest`
- `38 passed`

How to run locally:
- API: `.\.venv\Scripts\python.exe -m uvicorn src.adapters.api.main:app --reload`
- Dashboard: `.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py`
- Tests: `.\.venv\Scripts\python.exe -m pytest`
- Manual RemoteOK check: `.\.venv\Scripts\python.exe -c "from src.adapters.ingestion.remoteok import fetch_remoteok_jobs; print(fetch_remoteok_jobs(limit=2))"`

Interview explanation:
- I moved skill keywords from Python into `configs/skills.yaml` so the extraction step is easier to adjust without changing business logic.
- I kept skill extraction intentionally simple: it still uses readable keyword containment instead of NLP, embeddings, or complex matching.
- I improved the dashboard as a presentation layer only. It still reuses the existing pipeline and does not duplicate ingestion, cleaning, extraction, or analytics logic.
- I added RemoteOK as a separate ingestion adapter so real job data can enter the same raw job format as the sample data without changing downstream pipeline stages.
- I tested RemoteOK ingestion with fake HTTP clients because unit tests should be deterministic and should not fail because an external API is slow, unavailable, or changed.
- The architecture remains modular: ingestion brings data in, cleaning normalizes it, skill extraction enriches it, analytics counts it, and API/dashboard present the result.


---

## 2026-05-24

Today I worked on:
- `src/adapters/api/routes/skills.py` - made the skills endpoint source-aware
- `dashboard/app.py` - made the dashboard Source filter switch between sample data and RemoteOK
- `src/adapters/ingestion/remoteok.py` - added simple technical-role filtering for RemoteOK jobs
- `configs/skills.yaml` - expanded the existing config-driven skill list for real RemoteOK data
- `tests/adapters/api/test_skills.py` - added source parameter tests for the API
- `tests/adapters/ingestion/test_remoteok.py` - added tests for RemoteOK relevance filtering

What each piece does:
- `skills.py`: Adds a `source` query parameter to `GET /skills`. The default is still `sample`, and `remoteok` uses the existing RemoteOK ingestion adapter. Invalid sources return HTTP 400 with a clear message.
- `dashboard/app.py`: Shows `Sample data` and `RemoteOK` in the Source dropdown. The selected source is loaded first, then the same cleaning, skill extraction, and analytics flow runs.
- `remoteok.py`: Keeps RemoteOK ingestion responsible for fetching, filtering, and normalizing RemoteOK records. It now excludes obviously unrelated roles such as design, marketing, sales, support, customer success, recruiter, and product manager.
- `skills.yaml`: Keeps skill extraction configuration-driven, but expands the tracked skills beyond the original sample-focused list. The list now covers data engineering, backend/software engineering, cloud/devops, and data science/ML skills.
- `test_skills.py`: Verifies `source=sample`, mocked `source=remoteok`, and invalid source behavior without making live network calls.
- `test_remoteok.py`: Verifies technical RemoteOK jobs are kept, unrelated jobs are skipped, and filtering happens before the requested limit is applied.

Input:
- API query parameters:
  - `source=sample` or `source=remoteok`
  - `top_n`, still limited from 1 to 100
- Dashboard Source filter:
  - `Sample data`
  - `RemoteOK`
- `data/raw/sample_jobs.json` for the reliable local demo source
- `https://remoteok.com/api` for the experimental live RemoteOK source
- `configs/skills.yaml` for the configured skill keywords used by extraction

Output:
- `/skills?source=sample` returns skill counts from the local sample JSON file.
- `/skills?source=remoteok` returns skill counts from filtered RemoteOK jobs.
- The dashboard table, metrics, and chart update based on the selected source.
- RemoteOK records still use the same normalized raw job dictionary shape:
  `id`, `title`, `company`, `description`, `location`, `remote_type`, `source`, `source_url`, `posted_at`, `employment_type`, `seniority`, `tags`

Architecture changes:
- The API and dashboard are now source-aware at the adapter/presentation layer.
- The pipeline flow stays the same for both sources:
  ingestion -> cleaning -> skill extraction -> analytics
- Source selection does not add database logic, orchestration, Kafka, Spark, Redis, Airflow, or Supabase.
- RemoteOK relevance filtering belongs inside the RemoteOK ingestion adapter because this is where external raw records first enter SkillPulse.
- Sample data remains the reliable demo source. RemoteOK is available as an experimental live source, so its results can change depending on the public API response.

RemoteOK relevance filtering:
- The filter searches simple text from the RemoteOK title, tags, and description.
- It keeps technical/data/software-related roles such as data engineer, analytics engineer, ML engineer, backend engineer, software engineer, platform engineer, DevOps engineer, data scientist, Python developer, and full stack developer.
- It excludes clearly unrelated roles such as designer, marketing, sales, support, customer success, recruiter, and product manager.
- The logic is intentionally simple keyword matching so it is easy to read, test, and explain.

Skill configuration update:
- The original config-driven extraction approach stayed the same.
- The skill list now includes more practical real-data skills, such as `javascript`, `typescript`, `node`, `react`, `java`, `go`, `gcp`, `azure`, `kubernetes`, `terraform`, `numpy`, `pytorch`, `tensorflow`, and `machine learning`.
- Vague business keywords were avoided so irrelevant RemoteOK jobs are not treated as useful just because they contain generic words.

Edge cases handled:
- Missing sample file still returns a clear API error.
- Invalid source values return HTTP 400.
- RemoteOK network or HTTP failures return a clear upstream-source error through the API.
- RemoteOK metadata rows are skipped.
- Unrelated RemoteOK jobs are skipped before applying the requested result limit.
- Tests use fake clients or monkeypatching, so they do not depend on the live RemoteOK API.

Test result:
- `.\.venv\Scripts\python.exe -m py_compile src\adapters\ingestion\remoteok.py src\adapters\api\routes\skills.py dashboard\app.py`
- passed
- `.\.venv\Scripts\python.exe -m pytest tests/adapters/ingestion/test_remoteok.py tests/adapters/api/test_skills.py`
- `16 passed`
- `.\.venv\Scripts\python.exe -m pytest`
- `43 passed`

How to run locally:
- API: `.\.venv\Scripts\python.exe -m uvicorn src.adapters.api.main:app --reload`
- Sample API check: `http://127.0.0.1:8000/skills?source=sample&top_n=10`
- RemoteOK API check: `http://127.0.0.1:8000/skills?source=remoteok&top_n=10`
- Invalid source check: `http://127.0.0.1:8000/skills?source=linkedin`
- Dashboard: `.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py`

Interview explanation:
- I made source selection an adapter-level concern. The API and dashboard choose the source, but the core pipeline still receives raw job dictionaries and runs the same cleaning, extraction, and analytics steps.
- I kept sample data as the reliable demo path because it is local, stable, and deterministic. RemoteOK is useful for real-world practice, but it is an experimental live source because the public API can change or return different jobs each time.
- I added RemoteOK filtering inside ingestion because unrelated external jobs should be removed before they affect analytics. This keeps the dashboard focused on technical/data/software market intelligence.
- I expanded `skills.yaml` instead of hardcoding new skills in Python. That keeps skill extraction easy to adjust without changing pipeline code.
- I tested RemoteOK behavior with fake data so the test suite remains fast and reliable even when the live RemoteOK API is unavailable.
