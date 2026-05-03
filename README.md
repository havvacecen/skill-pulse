# SkillPulse

> **"Which skills does the job market actually demand?"**

SkillPulse is a modular data engineering platform that ingests job postings from multiple sources, extracts technical skill signals, and surfaces job-market intelligence through an API and dashboard.

---

## What It Does

- Collects job listings from sources like LinkedIn, Kariyer.net, and RemoteOK
- Cleans and normalizes raw posting data
- Extracts skill/technology mentions from job descriptions
- Aggregates skill trends by role, source, and time period
- Serves results through a FastAPI backend and a Streamlit dashboard

---

## Phase 1 Goal

> Validate the pipeline design using **sample/mock data** before connecting real sources.
> No real scrapers. No Kafka. No Spark. Just a clean, testable data flow from JSON → skills → trends.

---

## Project Structure

```
skill-pulse/
│
├── src/
│   ├── core/                   # Domain logic: schemas, constants, shared utilities
│   │   ├── common/             # Project-wide constants and path definitions
│   │   ├── schemas/            # Raw and processed job data models (Pydantic)
│   │   └── pipeline/           # Cleaning, normalization, and skill extraction logic
│   │
│   └── adapters/               # Everything that touches the outside world
│       ├── ingestion/          # Extractors that read from sample files or external sources
│       ├── storage/            # Writers that persist processed data to the database
│       └── api/                # FastAPI app: routes, services, and response schemas
│
├── data/
│   └── raw/                    # Raw input files; sample_jobs.json lives here in Phase 1
│
├── configs/
│   └── skills.yaml             # Skill keyword list used by the extraction step
│
├── dashboard/                  # Streamlit app: pages, charts, and API client
│
├── tests/                      # Mirrors src/ structure; one test module per source module
│
├── docs/                       # Architecture diagrams, data-flow notes, API contract
│
├── .env.example                # Required environment variables with placeholder values
└── requirements.txt            # Python dependencies
```

---

## Folder Responsibilities (one sentence each)

| Folder | Responsibility |
|---|---|
| `src/core/common` | Holds project-wide constants (source names, seniority levels) and `pathlib`-based path definitions that never change at runtime. |
| `src/core/schemas` | Defines the shape of data at each pipeline stage so that bad records are caught early with Pydantic validation. |
| `src/core/pipeline` | Contains all transformation logic — text normalization, cleaning rules, and keyword-based skill extraction. |
| `src/adapters/ingestion` | Reads raw job data from any source (sample file today, real APIs later) and returns a uniform list of raw job dicts. |
| `src/adapters/storage` | Writes cleaned and enriched job records to the database, keeping persistence concerns separate from business logic. |
| `src/adapters/api` | Exposes pipeline outputs through versioned FastAPI endpoints so the dashboard and external tools stay decoupled. |
| `data/raw` | Stores unmodified source data; nothing in this folder is ever written by the pipeline — only read. |
| `configs/` | Holds YAML-based configuration (skill lists, source definitions) that can change without touching Python code. |
| `dashboard/` | Presents skill trends, role comparisons, and remote ratios to end users through a Streamlit interface. |
| `tests/` | Mirrors `src/` so every module has a corresponding test file that can be run independently. |
| `docs/` | Stores architecture decisions, data-flow diagrams, and the API contract for reference and interview prep. |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Backend API | FastAPI |
| Dashboard | Streamlit |
| Database | PostgreSQL / Supabase |
| Orchestration | Airflow *(Phase 2+)* |
| Streaming | Kafka + Spark *(Phase 3+)* |

---

## Data Strategy

| Phase | Data Source | Purpose |
|---|---|---|
| Phase 1 | `data/raw/sample_jobs.json` | Validate pipeline design with static mock data |
| Phase 2 | `mock_job_producer.py` | Simulate ingestion without a real scraper |
| Phase 3 | RemoteOK API, public job feeds | Real data from live sources |

---

*This README reflects the Phase 1 structure. It will be updated as the project evolves.*
