"""
Simulates 'raw scraped' job postings data, deliberately messy:
- inconsistent salary formats
- missing values
- duplicate postings
- inconsistent location naming
- mixed date formats

This stands in for what you'd get from a real scrape/API pull, so the
cleaning step in clean_pipeline.py has real work to do.
"""
import random
import csv
import os
from datetime import datetime, timedelta

# Paths are relative to this script's location, so this works no matter
# what the repo folder is named or where it's cloned/extracted to
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = SCRIPT_DIR
os.makedirs(DATA_DIR, exist_ok=True)

random.seed(42)

titles = ["Data Scientist", "Data Analyst", "Junior Data Scientist", "Data Engineer",
          "Business Intelligence Analyst", "Machine Learning Engineer", "Data Science Intern",
          "Analytics Consultant", "Data Scientist II", "Insights Analyst"]

companies = ["Northwind Analytics", "BrightPath Retail", "Alderly Bank", "Kestrel Logistics",
             "Vantage Health", "Fenwick Insurance", "Orchard Media", "Solstice Energy",
             "Marlowe Consulting", "Redbridge Telecom", "Grove & Co", "Ashford Digital"]

locations_clean = ["London", "Manchester", "Birmingham", "Leeds", "Bristol", "Edinburgh",
                    "Remote", "Glasgow", "Liverpool", "Sheffield"]
# messy variants that will need cleaning
location_variants = {
    "London": ["London", "london", "LONDON", "London, UK", "Greater London"],
    "Manchester": ["Manchester", "manchester", "Manchester, UK"],
    "Remote": ["Remote", "remote", "Work from home", "WFH", "Remote (UK)"],
}

salary_bands = [(28000, 35000), (32000, 42000), (40000, 55000), (55000, 75000), (75000, 95000)]

def messy_salary(low, high):
    fmt = random.choice(["range", "range_k", "single", "missing", "text"])
    if fmt == "range":
        return f"£{low:,} - £{high:,}"
    if fmt == "range_k":
        return f"£{low//1000}k-£{high//1000}k"
    if fmt == "single":
        return f"£{(low+high)//2:,}"
    if fmt == "text":
        return "Competitive salary"
    return ""

def messy_date():
    d = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 500))
    fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%d %b %Y"])
    return d.strftime(fmt)

rows = []
seniority_band = {
    "Graduate": 0, "Junior": 0, "Mid": 2, "Senior": 4, "": 2,
}
london_uplift = 8000

for i in range(1, 1601):
    title = random.choice(titles)
    company = random.choice(companies)
    base_loc = random.choice(locations_clean)
    loc = random.choice(location_variants.get(base_loc, [base_loc]))
    seniority = random.choice(["Junior", "Mid", "Senior", "", "Graduate"])
    band_idx = min(seniority_band.get(seniority, 2) + random.choice([-1, 0, 0, 1]), len(salary_bands) - 1)
    band_idx = max(band_idx, 0)
    low, high = salary_bands[band_idx]
    if base_loc == "London":
        low, high = low + london_uplift, high + london_uplift
    salary = messy_salary(low, high)
    date_posted = messy_date()
    remote = random.choice(["Yes", "No", "Hybrid", "", "yes", "N/A"])
    rows.append([i, title, company, loc, salary, date_posted, remote, seniority])

# inject ~6% duplicate rows (same posting scraped twice) and some fully blank rows
for _ in range(90):
    rows.append(random.choice(rows[:1600]))
for _ in range(15):
    rows.append([len(rows)+1, "", "", "", "", "", "", ""])

random.shuffle(rows)

out_path = os.path.join(DATA_DIR, "raw_job_postings.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["posting_id", "title", "company", "location", "salary_raw", "date_posted_raw", "remote", "seniority"])
    w.writerows(rows)

print(f"Generated {len(rows)} raw rows -> {out_path}")
