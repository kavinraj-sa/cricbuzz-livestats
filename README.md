# 🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

A comprehensive cricket analytics dashboard that integrates live data from the Cricbuzz API with a SQLite database to deliver real-time match updates, player statistics, and SQL-driven analytics — all in an interactive Streamlit web application.

---

## 📸 Project Overview

| Page | What it does |
|------|-------------|
| 🏠 Home | Project overview and quick start guide |
| 🔴 Live Matches | Live scores, upcoming matches, recent results |
| 📊 Player Stats | ICC rankings, batting & bowling stats by format |
| 🔍 SQL Analytics | 25 pre-built SQL queries (beginner → advanced) |
| 🛠️ CRUD Operations | Add, view, update, delete players and matches |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core programming language |
| Streamlit | Interactive web UI |
| SQLite | Local database (no server needed) |
| Cricbuzz API | Live cricket data via RapidAPI |
| Pandas | Data display and manipulation |
| Requests | HTTP calls to the API |

---

## 📁 Project Structure

```
cricbuzz_project/
├── main.py                        ← App entry point + navigation
├── requirements.txt               ← Python dependencies
├── cricbuzz.db                    ← SQLite database (auto-created)
├── .gitignore                     ← Ignores db file and secrets
│
├── utils/
│   ├── db_connection.py           ← Database connection + table creation
│   └── api_helper.py              ← All Cricbuzz API functions
│
└── pages/
    ├── 1_Home.py                  ← Home / landing page
    ├── 2_Live_Matches.py          ← Live + upcoming + recent matches
    ├── 3_Player_Stats.py          ← ICC rankings + populate DB
    ├── 4_SQL_Analytics.py         ← 25 SQL queries with run button
    └── 5_CRUD_Operations.py       ← Create / Read / Update / Delete
```

---

## ⚙️ Setup Instructions

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/cricbuzz-livestats.git
cd cricbuzz-livestats
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Get your API key
1. Go to [RapidAPI Cricbuzz](https://rapidapi.com/cricketapilive/api/cricbuzz-cricket/)
2. Sign up for a free account
3. Subscribe to the free plan
4. Copy your API key

### Step 4 — Add your API key
Open `utils/api_helper.py` and replace:
```python
API_KEY = "YOUR_RAPIDAPI_KEY_HERE"
```
with your actual key.

### Step 5 — Set up the database
```bash
python utils/db_connection.py
```
This creates `cricbuzz.db` with all required tables and adds sample data.

### Step 6 — Run the app
```bash
streamlit run main.py
```
Your browser will open at `http://localhost:8501`

---

## 🗄️ Database Schema

The app uses **7 tables** in SQLite:

```
players        — player profiles (name, country, role, styles)
matches        — match records (teams, venue, result, toss)
venues         — cricket grounds (name, city, country, capacity)
series         — tournament/series info
batting_stats  — innings-level batting data per player
bowling_stats  — innings-level bowling data per player
fielding_stats — catches, stumpings, run-outs per player
```

### How data gets into the database

| Source | Tables filled |
|--------|--------------|
| "Save to DB" button on Live Matches page | matches |
| "Save all to DB" button on Player Stats page | players |
| "Populate DB" button on Player Stats page | players + matches + venues |
| CRUD → Create tab | players, matches, venues manually |

---

## 🔍 SQL Practice Questions

**25 queries across 3 difficulty levels:**

### 🟢 Beginner (Q1–Q8)
Basic SELECT, WHERE, GROUP BY, ORDER BY
- Q1: Indian players
- Q2: Recent matches
- Q3: Top 10 ODI run scorers
- Q4: Large venues (25,000+ capacity)
- Q5: Team win counts
- Q6: Players by role
- Q7: Highest score by format
- Q8: 2024 series

### 🟡 Intermediate (Q9–Q16)
JOINs, subqueries, aggregate functions
- Q9: All-rounders with 1000+ runs AND 50+ wickets
- Q10: Last 20 completed matches
- Q11: Multi-format player performance
- Q12: Home vs away win analysis
- Q13: 100+ run partnerships
- Q14: Bowler economy at venues
- Q15: Close match performers
- Q16: Yearly batting trends (2020+)

### 🔴 Advanced (Q17–Q25)
Window functions, CTEs, complex analytics
- Q17: Toss advantage analysis
- Q18: Most economical bowlers
- Q19: Most consistent batsmen
- Q20: Multi-format match count
- Q21: Overall performance ranking
- Q22: Head-to-head team analysis
- Q23: Player form categories
- Q24: Best batting partnerships
- Q25: Career trajectory analysis

---

## 📡 API Endpoints Used

| Category | Endpoints |
|----------|-----------|
| Matches | live, upcoming, recent, get-info, get-team, get-scorecard-v2, get-overs |
| Schedules | schedules/list |
| Series | list, archives, get-matches, get-players, get-venues, get-stats |
| Teams | list, get-players, get-results, get-schedules |
| Venues | get-info, get-matches |
| Players | list-trending, get-info, get-career, get-batting, get-bowling, search |
| Stats | get-icc-rankings (batting, bowling, allrounders) |

---

## 📦 Requirements

```
streamlit
requests
pandas
```

Install with:
```bash
pip install -r requirements.txt
```

---

## 🔒 Security Notes

- Never commit your API key to GitHub
- The `.gitignore` file excludes `cricbuzz.db` and any `.env` files
- Store your API key in an environment variable for production use

---

## 🚀 Future Improvements

- [ ] Add player search page using `players/search` endpoint
- [ ] Add match scorecard detail view
- [ ] Add team comparison page
- [ ] Add charts and visualizations for stats
- [ ] Deploy to Streamlit Cloud

---

## 📚 References

- [Cricbuzz API on RapidAPI](https://rapidapi.com/cricketapilive/api/cricbuzz-cricket/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [DB Browser for SQLite](https://sqlitebrowser.org/) — view your database visually

---

## 👤 Author

Built as part of a Data Analytics project using Python, SQL, and Streamlit.

**Domain:** Sports Analytics  
**Skills:** Python · SQL · Streamlit · REST API · Database Management
