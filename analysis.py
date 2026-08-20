"""
Analysis pass over the cleaned SQLite DB: answers a few concrete questions
a hiring analyst might actually ask, and saves a summary chart.
"""
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# All files (data, charts, database) are saved right next to this script,
# so there's no folder structure to worry about — everything reads/writes
# to whatever folder this script itself is sitting in.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "jobs.db")
OUT_DIR = SCRIPT_DIR

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM postings", conn)
conn.close()

print("=== Median salary by seniority ===")
print(df.groupby("seniority")["salary_mid"].median().sort_values(ascending=False))

print("\n=== Median salary by location (top 8 by count) ===")
top_locs = df["location"].value_counts().head(8).index
print(df[df["location"].isin(top_locs)].groupby("location")["salary_mid"].median().sort_values(ascending=False))

print("\n=== Remote work split ===")
print(df["remote"].value_counts(normalize=True).round(3))

print("\n=== Postings by title (top 10) ===")
print(df["title"].value_counts().head(10))

# Chart: median salary by seniority
fig, ax = plt.subplots(figsize=(7, 4.5))
order = ["Graduate", "Junior", "Mid", "Senior", "Unspecified"]
medians = df.groupby("seniority")["salary_mid"].median().reindex(order).dropna()
ax.bar(medians.index, medians.values, color="#3b6ea5")
ax.set_ylabel("Median advertised salary (£)")
ax.set_title("Median Data Science Salary by Seniority")
for i, v in enumerate(medians.values):
    ax.text(i, v + 500, f"£{v:,.0f}", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/salary_by_seniority.png", dpi=150)
print(f"\nSaved chart -> {OUT_DIR}/salary_by_seniority.png")
