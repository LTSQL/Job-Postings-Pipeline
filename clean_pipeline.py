"""
ETL pipeline: raw messy CSV -> cleaned, deduplicated, typed data -> SQLite DB.

Handles:
- inconsistent location naming (case, suffixes, WFH variants)
- inconsistent salary formats -> numeric salary_min / salary_max
- inconsistent date formats -> ISO dates
- duplicate postings
- missing/blank rows
"""
import re
import os
import sqlite3
import pandas as pd
from dateutil import parser as dateparser

# Paths are relative to this script's location, so this works no matter
# what the repo folder is named or where it's cloned/extracted to
# (e.g. "Job-Postings-Pipeline-main" after downloading a GitHub zip).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = SCRIPT_DIR

RAW_PATH = os.path.join(DATA_DIR, "raw_job_postings.csv")
DB_PATH = os.path.join(DATA_DIR, "jobs.db")
CLEAN_CSV_PATH = os.path.join(DATA_DIR, "clean_job_postings.csv")

LOCATION_MAP = {
    "london": "London", "greater london": "London",
    "manchester": "Manchester",
    "remote": "Remote", "work from home": "Remote", "wfh": "Remote",
}

def clean_location(loc):
    if not isinstance(loc, str) or loc.strip() == "":
        return None
    key = re.sub(r",?\s*uk$", "", loc.strip().lower()).strip()
    return LOCATION_MAP.get(key, loc.strip().title())

def parse_salary(raw):
    if not isinstance(raw, str) or raw.strip() == "":
        return None, None
    s = raw.replace(",", "").replace("£", "")
    if "competitive" in s.lower():
        return None, None
    nums = re.findall(r"(\d+)(k)?", s, flags=re.IGNORECASE)
    if not nums:
        return None, None
    values = [int(n) * (1000 if k else 1) for n, k in nums]
    if len(values) == 1:
        return values[0], values[0]
    return min(values), max(values)

def parse_date(raw):
    if not isinstance(raw, str) or raw.strip() == "":
        return None
    try:
        return dateparser.parse(raw, dayfirst=True).date().isoformat()
    except (ValueError, OverflowError):
        return None

def clean_remote(val):
    if not isinstance(val, str):
        return "Unknown"
    v = val.strip().lower()
    if v in ("yes", "y"):
        return "Yes"
    if v in ("no", "n"):
        return "No"
    if v == "hybrid":
        return "Hybrid"
    return "Unknown"

def run():
    df = pd.read_csv(RAW_PATH)

    # drop fully blank postings
    df = df.dropna(subset=["title", "company"], how="all")
    df = df[(df["title"].astype(str).str.strip() != "") & (df["company"].astype(str).str.strip() != "")]

    df["location_clean"] = df["location"].apply(clean_location)
    df[["salary_min", "salary_max"]] = df["salary_raw"].apply(lambda x: pd.Series(parse_salary(x)))
    df["date_posted"] = df["date_posted_raw"].apply(parse_date)
    df["remote_clean"] = df["remote"].apply(clean_remote)
    df["seniority_clean"] = df["seniority"].replace("", "Unspecified").fillna("Unspecified")

    # dedupe: same title+company+location+date is treated as the same posting
    before = len(df)
    df = df.drop_duplicates(subset=["title", "company", "location_clean", "date_posted"])
    removed = before - len(df)

    out = df[["posting_id", "title", "company", "location_clean", "salary_min", "salary_max",
              "date_posted", "remote_clean", "seniority_clean"]].rename(
        columns={"location_clean": "location", "remote_clean": "remote", "seniority_clean": "seniority"}
    )
    out["salary_mid"] = out[["salary_min", "salary_max"]].mean(axis=1)

    out.to_csv(CLEAN_CSV_PATH, index=False)

    conn = sqlite3.connect(DB_PATH)
    out.to_sql("postings", conn, if_exists="replace", index=False)
    conn.close()

    print(f"Raw rows: {before} | Duplicates removed: {removed} | Clean rows: {len(out)}")
    print(f"Missing salary after cleaning: {out['salary_mid'].isna().sum()} ({out['salary_mid'].isna().mean():.1%})")
    print(f"Wrote {CLEAN_CSV_PATH} and {DB_PATH}")

if __name__ == "__main__":
    run()
