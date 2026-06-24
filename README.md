<div align="center">

```
        🏟️  ESTADIO AZTECA  |  METLIFE STADIUM  |  AT&T STADIUM  🏟️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                                                    
         ⚽  FIFA WORLD CUP 2026  —  LIVE ANALYTICS PLATFORM  ⚽   
                                                                    
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              USA 🇺🇸  |  CANADA 🇨🇦  |  MEXICO 🇲🇽
```

[![Live Dashboard](https://img.shields.io/badge/⚽%20LIVE%20DASHBOARD-00b4ff?style=for-the-badge&logoColor=white)](https://fifa-wc-2026-analytics.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Azure SQL](https://img.shields.io/badge/Azure%20SQL-Cloud-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

**Real match data. Cloud database. Machine learning predictions. 10,000 simulated tournaments. Built live during the 2026 World Cup.**

[🏟️ Open Dashboard](https://fifa-wc-2026-analytics.streamlit.app) · [🐛 Report Bug](https://github.com/Sahil1021/fifa-wc-2026-analytics/issues)

</div>

---

## 🎯 What Is This?

A fully deployed end-to-end analytics platform tracking the FIFA World Cup 2026 in real time. Every day, match data is pulled from an API, stored in Azure SQL, fed into a machine learning model, and served through a live Streamlit dashboard.

Built from scratch during the tournament — not a tutorial project, not a demo dataset. Real data, real cloud, real predictions updating as the tournament unfolds.

---

## 🏗️ How It's Built

```
                    football-data.org API
                           │
                    fetch_data.py
                   (daily upsert pipeline)
                           │
              ┌────────────▼────────────┐
              │     Azure SQL Database   │
              │  ┌─────────────────────┐│
              │  │ teams       (48)    ││
              │  │ matches     (72)    ││
              │  │ predictions (48)    ││
              │  └─────────────────────┘│
              └────────────┬────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
    02_knockout_predictor.ipynb    Streamlit Dashboard
    ┌───────────────────────────┐  (fifa-wc-2026-analytics
    │ Random Forest Classifier  │   .streamlit.app)
    │ Monte Carlo Simulator     │
    │ 10,000 tournament sims    │
    └───────────────────────────┘
```

---

## ⚽ Dashboard Pages

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 Overview  │ 📊 Standings │ ⚽ Results │ 🔍 Team │ 📈 Trends │ 🏆 Predictions
└─────────────────────────────────────────────────────────────────┘
```

| Page | What You Get |
|------|-------------|
| 🏠 **Overview** | Live KPIs, goals by group, result distribution, top scorers, upset tracker |
| 📊 **Group Standings** | Live points table with gradient row colours — top 2 highlighted, third place contenders marked |
| ⚽ **Match Results** | Every result filterable by group and outcome, sortable by date |
| 🔍 **Team Deep Dive** | Form guide dots, match log, goals chart, group position, AI win probability |
| 📈 **Tournament Trends** | Daily goals timeline, confederation breakdown, upset tracker, group competitiveness |
| 🏆 **Predictions** | Podium display, top 10 bar chart, all 48 teams ranked by advancement probability |

---

## 🤖 The ML Model

### Random Forest + Monte Carlo Simulator

Two-stage prediction system:

**Stage 1 — Random Forest**
Trained on 2018 + 2022 World Cup data (80 historical records). Predicts probability of advancing from group stage based on:
- Points, goal difference, goals for/against
- Goals per game, win rate
- FIFA ranking (with Bayesian prior blending)
- Momentum score (recent form, weighted)

**Stage 2 — Monte Carlo Bracket Simulator**
Takes the group stage probabilities and simulates the entire knockout bracket 10,000 times:

```
For each of 10,000 simulations:
  1. Determine group qualifiers (probabilistic — upsets possible)
  2. Simulate R32 → R16 → QF → SF → Final
  3. Each match: stronger team wins with higher probability
     but upset factor (0.65 compression) keeps it realistic
  4. Record tournament winner

Final probability = wins / 10,000
```

This means bracket path matters. If Argentina and Brazil are on the same side, only one can reach the Final — their probabilities compete against each other directly.

**Key design decisions:**
- **Cold start handling** — FIFA ranking prior fades as matches played increases. Teams with 0 games played don't collapse to 0%.
- **Upsert pipeline** — not insert-only. Scores update when live matches finish, not just appended.
- **TLA fallback** — handles API code mismatches (e.g. `URU` vs `URY`).
- **Upset compression 0.65** — even the strongest team doesn't win 95% of simulated knockout matches. Football is unpredictable.

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Language | Python 3.13 |
| Database | Azure SQL (Spain Central) |
| ML | scikit-learn Random Forest |
| Simulation | NumPy Monte Carlo (10k runs) |
| Dashboard | Streamlit + Plotly |
| Data Source | football-data.org API |
| Deployment | Streamlit Cloud |

---

## 📁 Project Structure

```
fifa-wc-2026-analytics/
│
├── 📊 dashboard/
│   ├── app.py                        # Streamlit dashboard (6 pages)
│   └── wc26_logo1.png               # WC26 logo
│
├── 📓 notebooks/
│   ├── 01_exploratory_analysis.ipynb # EDA — goals, upsets, trends
│   └── 02_knockout_predictor.ipynb   # RF model + Monte Carlo simulator
│
├── ⚙️ scripts/
│   ├── fetch_data.py                 # Daily upsert pipeline
│   ├── create_schema.py             # Azure SQL schema setup
│   ├── create_predictions_table.py
│   ├── db_connection.py
│   └── verify_data.py
│
├── 📈 data/                          # Saved chart outputs
├── requirements.txt
└── .env                             # Not committed — Azure credentials
```

---

## 🚀 Run It Locally

```bash
# Clone
git clone https://github.com/Sahil1021/fifa-wc-2026-analytics.git
cd fifa-wc-2026-analytics

# Install
pip install -r requirements.txt

# Set up .env
DB_SERVER=your-server.database.windows.net
DB_NAME=your-db-name
DB_USERNAME=your-username
DB_PASSWORD=your-password

# Fetch live data
python scripts/fetch_data.py

# Run dashboard
cd dashboard
streamlit run app.py
```

---

## 🧠 What I Learned Building This

- **Upsert discipline** — an insert-only pipeline silently drops score updates. Painful to debug at 2am.
- **Cold start in ML** — blending a FIFA ranking prior prevents early-tournament predictions from collapsing.
- **Monte Carlo > static formulas** — France and Argentina in opposite bracket halves get very different probabilities even with similar group stage stats.
- **Streamlit + Azure on cloud** — dynamic IPs, stale connections, CSS specificity battles. All real production problems even at small scale.

---

## 👤 Built By

**Sahil Bhure**
MSc Business Analytics - Warwick Business School

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sahil-bhure/)
[![Dashboard](https://img.shields.io/badge/Live%20Dashboard-Open-00b4ff?style=flat-square&logo=streamlit&logoColor=white)](https://fifa-wc-2026-analytics.streamlit.app)

---

<div align="center">

```
🥇 France  |  🥈 England  |  🥉 Spain  |  ... or will Argentina surprise everyone? 🇦🇷
```

*Predictions update after every matchday. Check back after group stage.*

</div>
