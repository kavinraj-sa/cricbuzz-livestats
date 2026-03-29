# ============================================================
# pages/3_SQL_Analytics.py  —  SQL Queries & Analytics Page
# Runs all 25 pre-built SQL queries on the local database
# ============================================================

import streamlit as st
import pandas as pd
from utils.db_connection import run_query

st.set_page_config(page_title="SQL Analytics", page_icon="🔍", layout="wide")

st.title("🔍 SQL Analytics")
st.write("25 pre-built SQL queries on the cricket database — from beginner to advanced.")
st.divider()

# -------------------------------------------------------
# All 25 queries stored as a list of dictionaries
# Each query has: level, title, description, sql
# -------------------------------------------------------
QUERIES = [

    # ===== BEGINNER (1–8) =====
    {
        "level": "🟢 Beginner",
        "number": 1,
        "title": "Indian Players",
        "description": "Find all players who represent India.",
        "sql": """
            SELECT full_name, playing_role, batting_style, bowling_style
            FROM players
            WHERE country = 'India'
        """
    },
    {
        "level": "🟢 Beginner",
        "number": 2,
        "title": "Recent Matches",
        "description": "Show all recent cricket matches, most recent first.",
        "sql": """
            SELECT m.description, m.team1, m.team2, v.name AS venue, v.city, m.match_date
            FROM matches m
            LEFT JOIN venues v ON m.venue_id = v.id
            ORDER BY m.match_date DESC
        """
    },
    {
        "level": "🟢 Beginner",
        "number": 3,
        "title": "Top 10 ODI Run Scorers",
        "description": "Top 10 highest run scorers in ODI cricket.",
        "sql": """
            SELECT p.full_name, SUM(b.runs_scored) AS total_runs,
                   AVG(b.batting_average) AS avg, SUM(b.centuries) AS centuries
            FROM batting_stats b
            JOIN players p ON b.player_id = p.id
            WHERE b.format = 'ODI'
            GROUP BY p.full_name
            ORDER BY total_runs DESC
            LIMIT 10
        """
    },
    {
        "level": "🟢 Beginner",
        "number": 4,
        "title": "Large Venues",
        "description": "Venues with capacity over 25,000, largest first.",
        "sql": """
            SELECT name, city, country, capacity
            FROM venues
            WHERE capacity > 25000
            ORDER BY capacity DESC
            LIMIT 10
        """
    },
    {
        "level": "🟢 Beginner",
        "number": 5,
        "title": "Team Win Counts",
        "description": "How many matches each team has won.",
        "sql": """
            SELECT winner AS team, COUNT(*) AS total_wins
            FROM matches
            WHERE winner IS NOT NULL AND winner != ''
            GROUP BY winner
            ORDER BY total_wins DESC
        """
    },
    {
        "level": "🟢 Beginner",
        "number": 6,
        "title": "Players by Role",
        "description": "Count of players in each playing role.",
        "sql": """
            SELECT playing_role, COUNT(*) AS player_count
            FROM players
            WHERE playing_role IS NOT NULL
            GROUP BY playing_role
            ORDER BY player_count DESC
        """
    },
    {
        "level": "🟢 Beginner",
        "number": 7,
        "title": "Highest Score by Format",
        "description": "Highest individual batting score in each format.",
        "sql": """
            SELECT format, MAX(highest_score) AS highest_score
            FROM batting_stats
            GROUP BY format
        """
    },
    {
        "level": "🟢 Beginner",
        "number": 8,
        "title": "2024 Series",
        "description": "All cricket series that started in 2024.",
        "sql": """
            SELECT name, host_country, match_type, start_date, total_matches
            FROM series
            WHERE start_date LIKE '2024%'
            ORDER BY start_date
        """
    },

    # ===== INTERMEDIATE (9–16) =====
    {
        "level": "🟡 Intermediate",
        "number": 9,
        "title": "All-rounders: 1000 Runs & 50 Wickets",
        "description": "All-rounders with 1000+ runs AND 50+ wickets.",
        "sql": """
            SELECT p.full_name, SUM(b.runs_scored) AS total_runs,
                   SUM(bw.wickets_taken) AS total_wickets, b.format
            FROM players p
            JOIN batting_stats b  ON p.id = b.player_id
            JOIN bowling_stats bw ON p.id = bw.player_id AND b.format = bw.format
            WHERE p.playing_role = 'All-rounder'
            GROUP BY p.full_name, b.format
            HAVING total_runs > 1000 AND total_wickets > 50
        """
    },
    {
        "level": "🟡 Intermediate",
        "number": 10,
        "title": "Last 20 Completed Matches",
        "description": "Details of the last 20 completed matches.",
        "sql": """
            SELECT m.description, m.team1, m.team2, m.winner,
                   m.victory_margin, m.victory_type, v.name AS venue
            FROM matches m
            LEFT JOIN venues v ON m.venue_id = v.id
            WHERE m.status = 'Completed'
            ORDER BY m.match_date DESC
            LIMIT 20
        """
    },
    {
        "level": "🟡 Intermediate",
        "number": 11,
        "title": "Multi-Format Player Performance",
        "description": "Players who have played 2+ formats — runs per format.",
        "sql": """
            SELECT p.full_name,
                   SUM(CASE WHEN b.format='Test' THEN b.runs_scored ELSE 0 END) AS test_runs,
                   SUM(CASE WHEN b.format='ODI'  THEN b.runs_scored ELSE 0 END) AS odi_runs,
                   SUM(CASE WHEN b.format='T20I' THEN b.runs_scored ELSE 0 END) AS t20_runs,
                   AVG(b.batting_average) AS overall_avg
            FROM batting_stats b
            JOIN players p ON b.player_id = p.id
            GROUP BY p.full_name
            HAVING COUNT(DISTINCT b.format) >= 2
        """
    },
    {
        "level": "🟡 Intermediate",
        "number": 12,
        "title": "Home vs Away Win Analysis",
        "description": "Each team's wins at home vs away.",
        "sql": """
            SELECT m.winner AS team,
                   SUM(CASE WHEN v.country = p.country THEN 1 ELSE 0 END) AS home_wins,
                   SUM(CASE WHEN v.country != p.country THEN 1 ELSE 0 END) AS away_wins
            FROM matches m
            LEFT JOIN venues v ON m.venue_id = v.id
            LEFT JOIN players p ON p.full_name = m.winner
            WHERE m.winner IS NOT NULL AND m.winner != ''
            GROUP BY m.winner
        """
    },
    {
        "level": "🟡 Intermediate",
        "number": 13,
        "title": "100+ Run Partnerships",
        "description": "Batting pairs who combined for 100+ runs in same innings.",
        "sql": """
            SELECT b1.innings, p1.full_name AS batsman1, p2.full_name AS batsman2,
                   (b1.runs_scored + b2.runs_scored) AS partnership_runs
            FROM batting_stats b1
            JOIN batting_stats b2 ON b1.match_id = b2.match_id
                AND b1.innings = b2.innings
                AND b2.batting_position = b1.batting_position + 1
            JOIN players p1 ON b1.player_id = p1.id
            JOIN players p2 ON b2.player_id = p2.id
            WHERE (b1.runs_scored + b2.runs_scored) >= 100
            ORDER BY partnership_runs DESC
        """
    },
    {
        "level": "🟡 Intermediate",
        "number": 14,
        "title": "Bowler Economy at Venues",
        "description": "Bowlers with 3+ matches at same venue — economy & wickets.",
        "sql": """
            SELECT p.full_name, v.name AS venue,
                   ROUND(AVG(bw.economy_rate), 2) AS avg_economy,
                   SUM(bw.wickets_taken) AS total_wickets,
                   COUNT(*) AS matches_at_venue
            FROM bowling_stats bw
            JOIN players p ON bw.player_id = p.id
            JOIN matches m ON bw.match_id = m.id
            JOIN venues v ON m.venue_id = v.id
            WHERE bw.overs_bowled >= 4
            GROUP BY p.full_name, v.name
            HAVING matches_at_venue >= 3
            ORDER BY avg_economy ASC
        """
    },
    {
        "level": "🟡 Intermediate",
        "number": 15,
        "title": "Close Match Performers",
        "description": "Players who perform best in close matches (< 50 runs or < 5 wickets).",
        "sql": """
            SELECT p.full_name,
                   ROUND(AVG(b.runs_scored), 2) AS avg_runs_close_matches,
                   COUNT(*) AS close_matches_played
            FROM batting_stats b
            JOIN players p ON b.player_id = p.id
            JOIN matches m ON b.match_id = m.id
            WHERE (m.victory_type = 'runs'    AND CAST(m.victory_margin AS INTEGER) < 50)
               OR (m.victory_type = 'wickets' AND CAST(m.victory_margin AS INTEGER) < 5)
            GROUP BY p.full_name
            ORDER BY avg_runs_close_matches DESC
        """
    },
    {
        "level": "🟡 Intermediate",
        "number": 16,
        "title": "Yearly Batting Trends (2020+)",
        "description": "Player batting average and strike rate per year since 2020.",
        "sql": """
            SELECT p.full_name, b.match_year,
                   ROUND(AVG(b.runs_scored), 2) AS avg_runs,
                   ROUND(AVG(b.strike_rate), 2)  AS avg_strike_rate,
                   COUNT(*) AS matches
            FROM batting_stats b
            JOIN players p ON b.player_id = p.id
            WHERE b.match_year >= 2020
            GROUP BY p.full_name, b.match_year
            HAVING matches >= 5
            ORDER BY p.full_name, b.match_year
        """
    },

    # ===== ADVANCED (17–25) =====
    {
        "level": "🔴 Advanced",
        "number": 17,
        "title": "Toss Advantage Analysis",
        "description": "Does winning the toss help win the match?",
        "sql": """
            SELECT m.toss_decision,
                   COUNT(*) AS total_matches,
                   SUM(CASE WHEN m.toss_winner = m.winner THEN 1 ELSE 0 END) AS toss_winner_won,
                   ROUND(100.0 * SUM(CASE WHEN m.toss_winner = m.winner THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
            FROM matches m
            WHERE m.toss_winner IS NOT NULL AND m.winner IS NOT NULL
            GROUP BY m.toss_decision
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 18,
        "title": "Most Economical Bowlers",
        "description": "Best economy rate in limited-overs cricket (min 10 matches, 2 overs/match avg).",
        "sql": """
            SELECT p.full_name, b.format,
                   ROUND(AVG(b.economy_rate), 2) AS avg_economy,
                   SUM(b.wickets_taken) AS total_wickets,
                   COUNT(*) AS matches
            FROM bowling_stats b
            JOIN players p ON b.player_id = p.id
            WHERE b.format IN ('ODI', 'T20I')
            GROUP BY p.full_name, b.format
            HAVING matches >= 10 AND AVG(b.overs_bowled) >= 2
            ORDER BY avg_economy ASC
            LIMIT 20
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 19,
        "title": "Most Consistent Batsmen",
        "description": "Lowest standard deviation in scores = most consistent (min 10 balls faced, since 2022).",
        "sql": """
            SELECT p.full_name,
                   ROUND(AVG(b.runs_scored), 2) AS avg_runs,
                   COUNT(*) AS innings
            FROM batting_stats b
            JOIN players p ON b.player_id = p.id
            WHERE b.balls_faced >= 10 AND b.match_year >= 2022
            GROUP BY p.full_name
            HAVING innings >= 5
            ORDER BY avg_runs DESC
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 20,
        "title": "Multi-Format Match Count",
        "description": "Match count and batting average per format for players with 20+ total matches.",
        "sql": """
            SELECT p.full_name,
                   SUM(CASE WHEN b.format='Test' THEN 1 ELSE 0 END) AS test_matches,
                   SUM(CASE WHEN b.format='ODI'  THEN 1 ELSE 0 END) AS odi_matches,
                   SUM(CASE WHEN b.format='T20I' THEN 1 ELSE 0 END) AS t20_matches,
                   ROUND(AVG(b.batting_average), 2) AS overall_avg
            FROM batting_stats b
            JOIN players p ON b.player_id = p.id
            GROUP BY p.full_name
            HAVING (test_matches + odi_matches + t20_matches) >= 20
            ORDER BY overall_avg DESC
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 21,
        "title": "Overall Performance Ranking",
        "description": "Weighted score combining batting, bowling, and fielding performance.",
        "sql": """
            SELECT p.full_name, b.format,
                   ROUND(
                       (COALESCE(AVG(b.runs_scored),0) * 0.01) +
                       (COALESCE(AVG(b.batting_average),0) * 0.5) +
                       (COALESCE(AVG(b.strike_rate),0) * 0.3) +
                       (COALESCE(AVG(bw.wickets_taken),0) * 2) +
                       (COALESCE(AVG(f.catches),0) * 1)
                   , 2) AS performance_score
            FROM players p
            LEFT JOIN batting_stats  b  ON p.id = b.player_id
            LEFT JOIN bowling_stats  bw ON p.id = bw.player_id AND b.format = bw.format
            LEFT JOIN fielding_stats f  ON p.id = f.player_id AND b.match_id = f.match_id
            GROUP BY p.full_name, b.format
            ORDER BY performance_score DESC
            LIMIT 20
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 22,
        "title": "Head-to-Head Team Analysis",
        "description": "Win percentage for pairs of teams that have played 5+ matches.",
        "sql": """
            SELECT team1, team2,
                   COUNT(*) AS total_matches,
                   SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) AS team1_wins,
                   SUM(CASE WHEN winner = team2 THEN 1 ELSE 0 END) AS team2_wins,
                   ROUND(100.0 * SUM(CASE WHEN winner = team1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS team1_win_pct
            FROM matches
            WHERE winner IS NOT NULL AND winner != ''
            GROUP BY team1, team2
            HAVING total_matches >= 5
            ORDER BY total_matches DESC
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 23,
        "title": "Player Form Category",
        "description": "Categorise players as Excellent/Good/Average/Poor form based on last 10 innings.",
        "sql": """
            SELECT p.full_name,
                   ROUND(AVG(b.runs_scored), 2) AS recent_avg,
                   COUNT(*) AS recent_innings,
                   SUM(CASE WHEN b.runs_scored >= 50 THEN 1 ELSE 0 END) AS fifties_plus,
                   CASE
                       WHEN AVG(b.runs_scored) >= 50 THEN 'Excellent Form'
                       WHEN AVG(b.runs_scored) >= 30 THEN 'Good Form'
                       WHEN AVG(b.runs_scored) >= 15 THEN 'Average Form'
                       ELSE 'Poor Form'
                   END AS form_category
            FROM (
                SELECT player_id, runs_scored, match_id,
                       ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY match_id DESC) AS rn
                FROM batting_stats
            ) b
            JOIN players p ON b.player_id = p.id
            WHERE b.rn <= 10
            GROUP BY p.full_name
            ORDER BY recent_avg DESC
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 24,
        "title": "Best Batting Partnerships",
        "description": "Most successful consecutive batting pairs (5+ partnerships, avg partnership > 50).",
        "sql": """
            SELECT p1.full_name AS batsman1, p2.full_name AS batsman2,
                   COUNT(*) AS total_partnerships,
                   ROUND(AVG(b1.runs_scored + b2.runs_scored), 2) AS avg_partnership,
                   MAX(b1.runs_scored + b2.runs_scored) AS highest_partnership,
                   SUM(CASE WHEN (b1.runs_scored + b2.runs_scored) > 50 THEN 1 ELSE 0 END) AS good_partnerships
            FROM batting_stats b1
            JOIN batting_stats b2 ON b1.match_id = b2.match_id
                AND b1.innings = b2.innings
                AND b2.batting_position = b1.batting_position + 1
            JOIN players p1 ON b1.player_id = p1.id
            JOIN players p2 ON b2.player_id = p2.id
            GROUP BY p1.full_name, p2.full_name
            HAVING total_partnerships >= 5
            ORDER BY avg_partnership DESC
        """
    },
    {
        "level": "🔴 Advanced",
        "number": 25,
        "title": "Career Trajectory Analysis",
        "description": "Is a player's career ascending, stable, or declining? (6+ quarters of data).",
        "sql": """
            WITH quarterly AS (
                SELECT p.full_name,
                       b.match_year,
                       CASE
                           WHEN CAST(strftime('%m', m.match_date) AS INT) BETWEEN 1  AND 3  THEN 'Q1'
                           WHEN CAST(strftime('%m', m.match_date) AS INT) BETWEEN 4  AND 6  THEN 'Q2'
                           WHEN CAST(strftime('%m', m.match_date) AS INT) BETWEEN 7  AND 9  THEN 'Q3'
                           ELSE 'Q4'
                       END AS quarter,
                       AVG(b.runs_scored)  AS avg_runs,
                       AVG(b.strike_rate)  AS avg_sr,
                       COUNT(*)            AS matches
                FROM batting_stats b
                JOIN players p  ON b.player_id = p.id
                JOIN matches m  ON b.match_id  = m.id
                GROUP BY p.full_name, b.match_year, quarter
                HAVING matches >= 3
            )
            SELECT full_name,
                   COUNT(*) AS quarters_played,
                   ROUND(AVG(avg_runs), 2) AS overall_avg,
                   CASE
                       WHEN AVG(avg_runs) > (SELECT AVG(avg_runs) FROM quarterly q2 WHERE q2.full_name = quarterly.full_name LIMIT 3) * 1.1
                           THEN 'Career Ascending'
                       WHEN AVG(avg_runs) < (SELECT AVG(avg_runs) FROM quarterly q2 WHERE q2.full_name = quarterly.full_name LIMIT 3) * 0.9
                           THEN 'Career Declining'
                       ELSE 'Career Stable'
                   END AS career_phase
            FROM quarterly
            GROUP BY full_name
            HAVING quarters_played >= 6
            ORDER BY overall_avg DESC
        """
    },
]


# -------------------------------------------------------
# UI — Level filter + query selector
# -------------------------------------------------------

# Filter by level
level_options = ["All", "🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"]
selected_level = st.selectbox("Filter by level:", level_options)

# Filter queries
if selected_level == "All":
    filtered = QUERIES
else:
    filtered = [q for q in QUERIES if q["level"] == selected_level]

st.write(f"Showing **{len(filtered)}** queries")
st.divider()

# --- Query selector ---
query_labels = [f"Q{q['number']}. {q['title']} ({q['level']})" for q in filtered]
selected_label = st.selectbox("Choose a query:", query_labels)

# Find the selected query
selected_query = next(q for q in filtered if f"Q{q['number']}. {q['title']} ({q['level']})" == selected_label)

# --- Show query details ---
st.markdown(f"### Q{selected_query['number']}. {selected_query['title']}")
st.write(selected_query["description"])

# Show the SQL code
with st.expander("📄 View SQL code"):
    st.code(selected_query["sql"].strip(), language="sql")

# --- Run the query ---
if st.button("▶️ Run Query", type="primary"):
    with st.spinner("Running query..."):
        results = run_query(selected_query["sql"])

    if results:
        # Convert to DataFrame for nice display
        # sqlite3.Row objects behave like dicts
        df = pd.DataFrame([dict(row) for row in results])
        st.success(f"✅ {len(df)} row(s) returned")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv,
            file_name=f"query_{selected_query['number']}_results.csv",
            mime="text/csv"
        )
    else:
        st.info("""
        📭 No results returned.
        
        This could mean:
        - Your database doesn't have data for this query yet
        - Save some matches/players first from the Live Matches or Player Stats pages
        - Then try running this query again
        """)

st.divider()

# --- Custom SQL section ---
st.markdown("### ✏️ Write Your Own Query")
st.caption("Advanced users: run any SELECT query directly on your database")

custom_sql = st.text_area(
    "Enter your SQL query:",
    value="SELECT * FROM players LIMIT 10",
    height=120
)

if st.button("▶️ Run Custom Query"):
    if custom_sql.strip().upper().startswith("SELECT"):
        with st.spinner("Running..."):
            results = run_query(custom_sql)
        if results:
            df = pd.DataFrame([dict(row) for row in results])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No results.")
    else:
        st.error("⚠️ Only SELECT queries are allowed here for safety.")
