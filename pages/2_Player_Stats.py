# ============================================================
# pages/3_Player_Stats.py  —  Player Stats + Populate DB
# ============================================================

import streamlit as st
import pandas as pd
from utils.api_helper import (
    get_top_batting_stats, get_top_bowling_stats,
    get_match_scorecard, get_live_matches, get_recent_matches,
    save_player_to_db, save_match_to_db,
    save_batting_stat_to_db, save_bowling_stat_to_db
)
from utils.db_connection import run_query, run_command

st.title("📊 Player Stats")
st.write("ICC rankings fetched live from the Cricbuzz API.")
st.divider()

# ============================================================
# SECTION 1: POPULATE DATABASE
# ============================================================
with st.expander("🗄️ Populate Database — click here to fill your DB for SQL queries", expanded=False):
    st.markdown("""
    **Why do this?**
    The SQL Analytics page reads from your local `cricbuzz.db` file.
    Until you populate it, most SQL queries will return no results.

    **What gets saved when you populate:**
    - Players from ICC rankings → `players` table
    - Recent matches → `matches` table
    - Batting & bowling per innings → `batting_stats` / `bowling_stats` tables
    """)

    col1, col2 = st.columns(2)

    # ---- QUICK POPULATE ----
    with col1:
        st.markdown("#### Quick populate")
        st.caption("Fills players + matches — enough for Q1 to Q10")

        if st.button("⚡ Quick Populate", type="primary", key="quick_pop"):
            progress = st.progress(0, text="Starting...")

            progress.progress(10, text="Saving ODI rankings...")
            for p in get_top_batting_stats("odi"):
                save_player_to_db(p)
            for p in get_top_bowling_stats("odi"):
                save_player_to_db(p)

            progress.progress(35, text="Saving T20I rankings...")
            for p in get_top_batting_stats("t20i"):
                save_player_to_db(p)
            for p in get_top_bowling_stats("t20i"):
                save_player_to_db(p)

            progress.progress(55, text="Saving Test rankings...")
            for p in get_top_batting_stats("test"):
                save_player_to_db(p)
            for p in get_top_bowling_stats("test"):
                save_player_to_db(p)

            progress.progress(75, text="Saving recent matches...")
            for m in get_recent_matches():
                save_match_to_db(m)

            progress.progress(90, text="Saving live matches...")
            for m in get_live_matches():
                save_match_to_db(m)

            progress.progress(100, text="Done!")

            p_count = run_query("SELECT COUNT(*) as c FROM players")[0]["c"]
            m_count = run_query("SELECT COUNT(*) as c FROM matches")[0]["c"]
            st.success(f"✅ Saved {p_count} players and {m_count} matches!")
            st.info("Go to SQL Analytics and try Q1–Q10 now!")

    # ---- FULL POPULATE ----
    with col2:
        st.markdown("#### Full populate")
        st.caption("Also fills batting_stats + bowling_stats — needed for Q11 to Q25")
        st.warning("⚠️ Takes 2–3 minutes (many API calls)")

        if st.button("🔄 Full Populate", key="full_pop"):
            progress = st.progress(0, text="Starting full populate...")

            # Save players from all formats
            progress.progress(5, text="Saving players from all formats...")
            for fmt in ["odi", "t20i", "test"]:
                for p in get_top_batting_stats(fmt):
                    save_player_to_db(p)
                for p in get_top_bowling_stats(fmt):
                    save_player_to_db(p)

            # Save recent matches
            progress.progress(20, text="Saving recent matches...")
            recent = get_recent_matches()
            for m in recent:
                save_match_to_db(m)

            # Fetch scorecards and save batting/bowling stats
            saved_stats = 0
            for i, match in enumerate(recent[:15]):  # max 15 to avoid rate limits
                match_id = match.get("match_id", "")
                if not match_id:
                    continue

                pct = 25 + int((i / 15) * 70)
                progress.progress(pct, text=f"Scorecard {i+1}/15: {match.get('team1','')} vs {match.get('team2','')}...")

                innings_list = get_match_scorecard(match_id)
                if not innings_list:
                    continue

                db_match = run_query(
                    "SELECT id FROM matches WHERE description = ? AND team1 = ?",
                    (match.get("description",""), match.get("team1",""))
                )
                if not db_match:
                    continue

                match_db_id = db_match[0]["id"]
                fmt = match.get("format", "T20").upper()

                for innings in innings_list:
                    for bat in innings.get("batting", []):
                        db_player = run_query(
                            "SELECT id FROM players WHERE full_name LIKE ?",
                            (f"%{bat.get('name','')}%",)
                        )
                        if db_player:
                            save_batting_stat_to_db(db_player[0]["id"], match_db_id, bat, fmt)
                            saved_stats += 1

                    for bowl in innings.get("bowling", []):
                        db_player = run_query(
                            "SELECT id FROM players WHERE full_name LIKE ?",
                            (f"%{bowl.get('name','')}%",)
                        )
                        if db_player:
                            save_bowling_stat_to_db(db_player[0]["id"], match_db_id, bowl, fmt)
                            saved_stats += 1

            progress.progress(100, text="Done!")

            p_count  = run_query("SELECT COUNT(*) as c FROM players")[0]["c"]
            m_count  = run_query("SELECT COUNT(*) as c FROM matches")[0]["c"]
            bs_count = run_query("SELECT COUNT(*) as c FROM batting_stats")[0]["c"]
            bw_count = run_query("SELECT COUNT(*) as c FROM bowling_stats")[0]["c"]

            st.success(f"✅ Full populate complete!\n\n"
                       f"Players: {p_count} | Matches: {m_count} | "
                       f"Batting stats: {bs_count} | Bowling stats: {bw_count}")
            st.info("All 25 SQL queries should now return results!")

    # ---- DB STATUS ----
    st.markdown("#### Current database status")
    try:
        counts = {
            "Players":       run_query("SELECT COUNT(*) as c FROM players")[0]["c"],
            "Matches":       run_query("SELECT COUNT(*) as c FROM matches")[0]["c"],
            "Venues":        run_query("SELECT COUNT(*) as c FROM venues")[0]["c"],
            "Batting stats": run_query("SELECT COUNT(*) as c FROM batting_stats")[0]["c"],
            "Bowling stats": run_query("SELECT COUNT(*) as c FROM bowling_stats")[0]["c"],
        }
        cols = st.columns(5)
        for col, (label, val) in zip(cols, counts.items()):
            col.metric(label, val)

        if counts["Players"] == 0:
            st.warning("⚠️ Database is empty — click Quick Populate above!")
        elif counts["Batting stats"] == 0:
            st.info("ℹ️ Basic data loaded. Use Full Populate to also save batting/bowling stats.")
        else:
            st.success("✅ Database has data — SQL queries should work!")
    except Exception as e:
        st.error(f"Error reading DB: {e}")

st.divider()

# ============================================================
# SECTION 2: ICC RANKINGS (live from API)
# ============================================================
st.markdown("## ICC Rankings")
st.caption("Live data from the Cricbuzz API — refreshes every time you load this page")

format_choice   = st.radio("Format:", ["ODI", "Test", "T20I"], horizontal=True)
format_map      = {"ODI": "odi", "Test": "test", "T20I": "t20i"}
selected_format = format_map[format_choice]

col_bat, col_bowl = st.columns(2)

with col_bat:
    st.markdown("### 🏏 Top Batsmen")
    if st.button("🔄 Refresh", key="refresh_bat"):
        st.rerun()
    with st.spinner("Loading batting rankings..."):
        batsmen = get_top_batting_stats(selected_format)
    if batsmen:
        if st.button("💾 Save to DB", key="save_bat"):
            for p in batsmen:
                save_player_to_db(p)
            st.success(f"Saved {len(batsmen)} players!")
        df = pd.DataFrame(batsmen)
        df = df.rename(columns={"rank":"Rank","name":"Player","country":"Country","rating":"Rating"})
        df = df.drop(columns=["player_id"], errors="ignore")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("#### Rating comparison (Top 10)")
        st.bar_chart(df.head(10).set_index("Player")["Rating"])
    else:
        st.warning("Could not load. Check your API key in utils/api_helper.py.")

with col_bowl:
    st.markdown("### 🎳 Top Bowlers")
    if st.button("🔄 Refresh", key="refresh_bowl"):
        st.rerun()
    with st.spinner("Loading bowling rankings..."):
        bowlers = get_top_bowling_stats(selected_format)
    if bowlers:
        if st.button("💾 Save to DB", key="save_bowl"):
            for p in bowlers:
                save_player_to_db(p)
            st.success(f"Saved {len(bowlers)} players!")
        df = pd.DataFrame(bowlers)
        df = df.rename(columns={"rank":"Rank","name":"Player","country":"Country","rating":"Rating"})
        df = df.drop(columns=["player_id"], errors="ignore")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("#### Rating comparison (Top 10)")
        st.bar_chart(df.head(10).set_index("Player")["Rating"])
    else:
        st.warning("Could not load. Check your API key in utils/api_helper.py.")

st.divider()

# ============================================================
# SECTION 3: PLAYERS IN YOUR DATABASE
# ============================================================
st.markdown("## 🗄️ Players in your database")
st.caption("These are the players your SQL queries can analyse")

db_players = run_query("""
    SELECT full_name AS Name, country AS Country,
           playing_role AS Role, batting_style AS Batting,
           bowling_style AS Bowling
    FROM players ORDER BY country, full_name
""")

if db_players:
    df_db = pd.DataFrame([dict(r) for r in db_players])
    countries = ["All"] + sorted(df_db["Country"].dropna().unique().tolist())
    selected_country = st.selectbox("Filter by country:", countries)
    if selected_country != "All":
        df_db = df_db[df_db["Country"] == selected_country]
    st.dataframe(df_db, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(df_db)} players")
else:
    st.info("No players yet. Use the Populate Database section above to get started!")
