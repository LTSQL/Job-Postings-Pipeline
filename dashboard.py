"""
Streamlit dashboard over the cleaned job postings DB.
Run with: streamlit run src/dashboard.py
"""
import os
import sqlite3
import pandas as pd
import streamlit as st

# All files (data, charts, database) are saved right next to this script,
# so there's no folder structure to worry about — everything reads/writes
# to whatever folder this script itself is sitting in.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "jobs.db")

st.set_page_config(page_title="UK Data Science Job Market", layout="wide")

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM postings", conn)
    conn.close()
    return df

df = load_data()

st.title("UK Data Science Job Market — Postings Dashboard")
st.caption("Built from a cleaned ETL pipeline (raw scrape -> cleaning -> SQLite -> this dashboard).")

col1, col2, col3 = st.columns(3)
col1.metric("Total postings (cleaned)", len(df))
col2.metric("Median salary", f"£{df['salary_mid'].median():,.0f}")
col3.metric("% remote or hybrid", f"{df['remote'].isin(['Yes','Hybrid']).mean():.0%}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Median salary by seniority")
    order = ["Graduate", "Junior", "Mid", "Senior", "Unspecified"]
    med = df.groupby("seniority")["salary_mid"].median().reindex(order).dropna()
    st.bar_chart(med)

with right:
    st.subheader("Postings by location")
    st.bar_chart(df["location"].value_counts().head(10))

st.divider()
st.subheader("Filter postings")
title_filter = st.multiselect("Job title", sorted(df["title"].dropna().unique()))
loc_filter = st.multiselect("Location", sorted(df["location"].dropna().unique()))

filtered = df.copy()
if title_filter:
    filtered = filtered[filtered["title"].isin(title_filter)]
if loc_filter:
    filtered = filtered[filtered["location"].isin(loc_filter)]

st.dataframe(filtered[["title", "company", "location", "salary_min", "salary_max", "date_posted", "remote", "seniority"]],
             use_container_width=True)
