# UK Data Science Job Market — End-to-End Pipeline
 
**Business question:** What does the current UK data science job market look like — pay by seniority and location, and how common is remote work — and can that be tracked reliably over time from raw postings data?
 
## Why this project
 
Most student projects start from a clean Kaggle CSV. This one starts from date deliberately messy, realistic raw data (inconsistent salary formats, mixed date formats, inconsistent location naming, duplicate postings, missing fields) and builds the full pipeline needed to make it usable. That mirrors what a data analyst actually spends most of their time doing.
 
## Pipeline
 
```
raw_job_postings.csv → clean_pipeline.py → jobs.db (SQLite) + clean_job_postings.csv → analysis.py / dashboard.py
```
 
1. **`generate_raw_data.py`** — generates a realistic messy raw dataset (stands in for a scrape/API pull). Salary bands are correlated with seniority and location, as they would be in reality, so the analysis has genuine signal to find.
2. **`clean_pipeline.py`** — the core ETL step:
   - Normalises location naming (`london`, `LONDON`, `London, UK` → `London`)
   - Parses inconsistent salary formats (`£40k-£55k`, `£40,000 - £55,000`, `Competitive`) into numeric `salary_min` / `salary_max`
   - Parses mixed date formats into ISO dates
   - Deduplicates postings scraped more than once
   - Loads the result into a SQLite database (`data/jobs.db`) and a clean CSV
3. **`analysis.py`** — answers concrete questions (median salary split by seniority/location, remote work split, most common titles) and saves a summary chart to `outputs/`
4. **`dashboard.py`** — an interactive Streamlit dashboard over the cleaned database, with filtering by title and location
## How to run
 
```bash
pip install pandas numpy python-dateutil matplotlib streamlit
 
python FileLocation\generate_raw_data.py     # creates raw_job_postings.csv
python FileLocation\clean_pipeline.py        # creates jobs.db + clean_job_postings.csv
python FileLocation\analysis.py              # prints summary stats, saves outputs/salary_by_seniority.png
streamlit run FileLocation\dashboard.py      # interactive dashboard
```
 
## Key findings (from this run)
 
- Cleaning removed ~91 duplicate postings out of ~1,690 raw rows (~5.4%).
- Even after cleaning, ~40% of postings still had no usable salary figure — a real finding worth flagging, not hiding: salary transparency in these postings is inconsistent.
- Median advertised salary for Senior roles was roughly 2.7x Graduate/Junior roles.
- London postings carried a consistent salary premium over other UK cities.
- About a third of postings were remote, with hybrid a further ~17%.
## What I'd do with more time
 
- Swap the synthetic generator for a real API/scrape source (e.g. a job board API) — the cleaning and analysis layers are already written to be source-agnostic.
- Add a scheduled run (`cron`/GitHub Actions) so the dashboard shows trends over time, not just a snapshot.
- Add data validation checks (e.g. with `pandera`) so bad data fails loudly instead of silently passing through.

 
