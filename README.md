<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:003eb3,100:00b4ff&height=200&section=header&text=FIFA%20World%20Cup%202026&fontSize=42&fontColor=ffffff&fontAlignY=38&desc=Live%20Analytics%20Dashboard&descAlignY=58&descSize=20&descColor=rgba(255,255,255,0.8)" width="100%"/>

[![Live Demo](https://img.shields.io/badge/Live%20Dashboard-00b4ff?style=for-the-badge&logo=streamlit&logoColor=white)](https://fifa-wc-2026-analytics.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Azure SQL](https://img.shields.io/badge/Azure%20SQL-Cloud%20DB-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**An end-to-end data analytics platform built during the live FIFA World Cup 2026 tournament. Real match data, cloud database, ML predictions, deployed dashboard.**

[View Live Dashboard](https://fifa-wc-2026-analytics.streamlit.app) · [Report Bug](https://github.com/Sahil1021/fifa-wc-2026-analytics/issues)

</div>

---

## What This Is

A fully deployed analytics platform that ingests live World Cup match data, stores it in Azure SQL, runs a Random Forest model to predict tournament winners, and serves everything through a custom Streamlit dashboard — built entirely during the tournament.

---

## Architecture

```
football-data.org API
        │
        ▼
  fetch_data.py  ──────────────────────────────────────────┐
  (upsert pipeline)                                         │
        │                                                   │
        ▼                                                   ▼
  Azure SQL Database (fifa-wc-db)              02_knockout_predictor.ipynb
  ├── teams (48 rows)                          (Random Forest model)
  ├── matches (72 fixtures)                            │
  ├── group_standings                                  │
  └── predictions (48 rows) ◄───────────────────────┘
        │
        ▼
  Streamlit Dashboard
  (fifa-wc-2026-analytics.streamlit.app)
```

---

## Dashboard Pages

| Page | What's in it |
|------|-------------|
| 🏠 Overview | Live KPIs, goals by group, result distribution, top scorers, upset tracker |
| 📊 Group Standings | Custom HTML tables with gradient row colours by position, live points |
| ⚽ Match Results | Filterable by group and result type, sortable by date |
| 🔍 Team Deep Dive | Form guide, match log, goals chart, group position, AI prediction |
| 📈 Tournament Trends | Daily goals timeline, confederation analysis, upset tracker, group competitiveness |
| 🏆 Predictions | Podium display, bar chart top 10, group advancement probabilities |

---

## ML Model

**Random Forest Classifier** trained on historical World Cup data (2018 + 2022).

**Features used:**
- Points from group stage matches (live from Azure SQL)
- Goal difference, goals for, goals per game
- FIFA ranking (with Bayesian prior blending)
- Momentum score (recent form weighted)

**Key design decisions:**
- **Cold start handling** — FIFA ranking floor that fades as matches played increases. Stops unplayed teams from getting 0% probability.
- **Upsert pipeline** — not insert-only. Scores update correctly when live matches finish.
- **TLA fallback** — handles mismatches between API codes and internal DB values (e.g. URU vs URY).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| Database | Azure SQL (Spain Central) |
| ML | scikit-learn Random Forest |
| Dashboard | Streamlit + Plotly |
| Data Source | football-data.org API |
| Deployment | Streamlit Cloud |
| Environment | Anaconda, VS Code |

---

## Project Structure

```
fifa-wc-2026-analytics/
├── dashboard/
│   ├── app.py                    # Main Streamlit dashboard
│   └── wc26_logo1.png            # WC26 logo asset
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb    # EDA — 12 cells
│   └── 02_knockout_predictor.ipynb      # ML model + saves to Azure SQL
├── scripts/
│   ├── fetch_data.py             # Daily data pipeline (upsert)
│   ├── create_schema.py          # Azure SQL schema setup
│   ├── create_predictions_table.py
│   ├── db_connection.py
│   └── verify_data.py
├── data/                         # Saved chart outputs
├── requirements.txt
└── .env                          # Not committed — Azure credentials
```

---

## Setup & Run Locally

**Prerequisites:** Python 3.10+, ODBC Driver 17 for SQL Server, Azure SQL access

```bash
# Clone
git clone https://github.com/Sahil1021/fifa-wc-2026-analytics.git
cd fifa-wc-2026-analytics

# Install dependencies
pip install -r requirements.txt

# Create .env file
DB_SERVER=your-server.database.windows.net
DB_NAME=your-db-name
DB_USERNAME=your-username
DB_PASSWORD=your-password

# Set up schema and fetch data
python scripts/create_schema.py
python scripts/fetch_data.py

# Run dashboard
cd dashboard
streamlit run app.py
```

---

## Key Learnings

- **Upsert discipline** — insert-only pipelines silently fail for live data. Match scores need UPDATE logic not just INSERT.
- **Cold start ML** — blending a FIFA ranking prior with model output prevents early-tournament predictions collapsing to zero for unplayed teams.
- **Cloud deployment** — Azure firewall rules, dynamic IPs, and stale connection handling are real production concerns even for small projects.
- **CSS specificity in Streamlit** — Streamlit's internal inline styles require `!important` overrides and sometimes direct `data-testid` selectors to override reliably.

---

## Built By

**Sahil Bhure**  
MSc Business Analytics — Warwick Business School  
BSc Data Science — IIT Madras

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/sahilbhure)
[![Live Dashboard](https://img.shields.io/badge/Dashboard-Live-00b4ff?style=flat-square&logo=streamlit&logoColor=white)](https://fifa-wc-2026-analytics.streamlit.app)

---

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00b4ff,100:003eb3&height=100&section=footer" width="100%"/>
</div>