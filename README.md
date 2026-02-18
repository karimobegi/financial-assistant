# Personal Finance Assistant

A full-stack personal finance analysis application built with **FastAPI**, **Pandas**, and **SQLite**.  
Users upload a bank transaction CSV and receive structured spending analysis and human-readable financial advice through a web interface.

🔗 **Live Demo:**  
https://my-projects-mf93.onrender.com/
_(Free-tier deployment — first load may take ~30 seconds)_

---

## Overview

This project implements an end-to-end personal finance analysis pipeline exposed through a REST API and a lightweight frontend.

It ingests raw bank transaction CSV exports, cleans and categorizes transactions, persists them into a SQLite database, performs analytical aggregation using Pandas, and generates concise rule-based financial insights.

The goal of the project is to demonstrate:

- data engineering fundamentals
- backend API design
- analytical reasoning
- clean software architecture
- end-to-end deployment

---

## Features

### Backend

- Upload bank CSV files
- Clean and normalize transaction data
- Categorize transactions using rule-based logic
- Persist transactions into SQLite
- Analyze spending by category and by month
- Detect unusually large transactions (outliers)
- Compute income, expenses, and net savings
- Generate human-readable financial advice
- JSON-safe API responses
- Idempotent pipeline execution (`run-all`)
- Optional database reset

### Frontend

- Simple HTML / CSS / JavaScript interface
- CSV upload
- One-click pipeline execution
- Displays analysis results and advice

### Deployment

- FastAPI backend deployed on Render
- Frontend served by FastAPI
- Public demo URL

---

## Project Structure

```text
financial-assistant-project/
├── src/
│   ├── api.py              # FastAPI application
│   ├── ingest.py           # CSV ingestion & cleaning
│   ├── persist.py          # SQLite persistence
│   ├── analysis.py         # Pandas-based analysis
│   ├── safe_analysis.py    # JSON-safe serialization
│   ├── advice.py           # Rule-based advice
│   ├── db.py               # DB setup, stats, reset
│   └── Website/
│       ├── index.html      # Frontend UI
│       ├── style.css
│       └── script.js
├── data/
│   ├── uploads/            # Uploaded CSVs (gitignored)
│   ├── clean_transactions.csv
│   └── finance.db
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Pipeline Phases

### Phase 1 — Ingestion & Cleaning

- Reads raw bank transaction CSVs
- Normalizes merchant names
- Converts amounts to numeric values
- Computes absolute transaction values
- Assigns spending categories
- Outputs a clean, standardized CSV

### Phase 2 — Persistence

- Stores cleaned transactions in SQLite
- Prevents duplicate inserts via constraints

### Phase 3 — Analysis

- Computes totals and averages by category
- Calculates spending percentages
- Analyzes spending over time
- Identifies unusually large transactions
- Computes monthly cashflow and savings

### Phase 4 — Advice

- Interprets analysis results using rule-based logic
- Produces concise, human-readable insights
- Handles insufficient or partial data gracefully

### Phase 5 — FastAPI

- Exposes the full pipeline via REST endpoints
- Uploads CSV files using multipart form data
- Returns JSON-safe analytical results
- Provides a single `/run-all` endpoint for full execution

### Phase 6 — Frontend

- Lightweight HTML / CSS / JavaScript UI
- Allows CSV upload and DB reset
- Displays analysis output and advice

### Phase 7 — Deployment

- Deployed on Render (free tier)
- Backend and frontend served together
- Public demo link available

---

## Input

The application expects a **CSV export from a bank**, typically containing:

- `date`
- `merchant`
- `amount`
- `category` _(optional — inferred if missing)_

Formatting differences are handled during ingestion.

---

## Notes

- This project is intended for learning and demonstration purposes
- No real personal financial data should be committed
- Free-tier deployments may experience cold starts
