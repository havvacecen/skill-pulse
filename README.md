# SkillPulse

> **"Which skills does the job market actually demand?"**

SkillPulse is a modular data engineering project that loads sample job postings, cleans and enriches them, extracts technical skill signals, and serves job-market insights through a FastAPI API and a Streamlit dashboard.

---

## What It Does

- Loads sample job records from `data/raw/sample_jobs.json`
- Cleans and normalizes raw job fields
- Extracts skill mentions from job titles and descriptions
- Counts the most frequently requested skills
- Exposes skill counts through FastAPI
- Displays filtered skill insights in Streamlit

---

## Architecture Flow

```text
data/raw/sample_jobs.json
        |
        v
Ingestion
load raw job records
        |
        v
Cleaning
normalize job fields
        |
        v
Skill Extraction
add extracted_skills to each job
        |
        v
Analytics
count and sort extracted skills
        |
        +--------------------+
        |                    |
        v                    v
FastAPI API           Streamlit Dashboard
/health, /skills      filters, metrics, table, chart
```

The API and dashboard both reuse the same core pipeline logic. The dashboard currently runs the pipeline directly in memory; it does not call the API yet.

---

## Project Structure

```text
skill-pulse/
|
├── configs/
│   └── skills.yaml
|
├── dashboard/
│   └── app.py
|
├── data/
│   └── raw/
│       └── sample_jobs.json
|
├── docs/
│   ├── learning-log.md
|
├── src/
│   ├── adapters/
│   │   ├── api/
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       └── skills.py
│   │   └── ingestion/
│   │       └── ingestion.py
│   │
│   └── core/
│       ├── analytics/
│       │   └── skill_counts.py
│       └── pipeline/
│           ├── cleaning.py
│           └── skill_extraction.py
|
├── tests/
│   └── adapters/
│       ├── api/
│       ├── core/
│       └── ingestion/
|
├── .env.example
├── conftest.py
├── README.md
└── requirements.txt
```

---

## Pipeline Explanation

| Stage | Responsibility |
|---|---|
| Ingestion | Reads `data/raw/sample_jobs.json` and returns raw job dictionaries. |
| Cleaning | Normalizes job records so downstream processing receives consistent text. |
| Skill extraction | Finds configured skill keywords in cleaned job titles and descriptions, then adds `extracted_skills`. |
| Analytics | Counts extracted skills and returns sorted frequency results. |
| API | Runs the pipeline in memory and returns skill data through FastAPI endpoints. |
| Dashboard | Runs the same pipeline in memory and shows filters, metric cards, a table, and a chart in Streamlit. |

This separation keeps the project modular: each stage has one clear job and can be tested independently.

---

## Run Locally

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run tests:

```powershell
python -m pytest
```

Run the FastAPI app:

```powershell
python -m uvicorn src.adapters.api.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Run the Streamlit dashboard in a second terminal:

```powershell
python -m streamlit run dashboard/app.py
```

---

## API Endpoints

### `GET /health`

Checks whether the API server is running.

Example response:

```json
{
  "status": "ok"
}
```

### `GET /skills`

Runs the current in-memory pipeline and returns the top skill counts from the sample job dataset.

Query parameters:

| Parameter | Type | Default | Rules | Description |
|---|---:|---:|---|---|
| `top_n` | integer | `10` | `1` to `100` | Number of top skills to return. |

Example request:

```text
GET /skills?top_n=3
```

Example response:

```json
{
  "skills": [
    {
      "skill": "python",
      "count": 12
    },
    {
      "skill": "sql",
      "count": 11
    },
    {
      "skill": "aws",
      "count": 8
    }
  ]
}
```

Invalid `top_n` values such as `0` or `101` return FastAPI validation errors.

---

## Dashboard

The Streamlit dashboard reuses the existing pipeline directly:

```text
load_jobs -> clean_job -> enrich_job_with_skills -> get_skill_counts
```

Current dashboard features:

- Role filter
- Source filter
- Remote / Hybrid / Onsite filter
- Seniority filter
- Posted date range filter
- Top-N slider
- Total jobs metric
- Unique skills metric
- Remote ratio metric
- Top skills table and bar chart

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| API | FastAPI |
| Dashboard | Streamlit |
| Testing | pytest |
| Data source | Local sample JSON |

---

## Current Data Strategy

| Data Source | Purpose |
|---|---|
| `data/raw/sample_jobs.json` | Validate the end-to-end pipeline with static sample job records before adding real ingestion sources. |

This README reflects the current implemented project state.
