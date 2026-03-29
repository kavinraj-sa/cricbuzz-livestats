# ============================================================
# pages/2_Player_Stats.py  —  Top Player Stats Page
# Shows top batting and bowling rankings by format
# ============================================================

import streamlit as st
import pandas as pd
from utils.api_helper import get_top_batting_stats, get_top_bowling_stats, save_player_to_db

st.set_page_config(page_title="Player Stats", page_icon="📊", layout="wide")

st.title("📊 Top Player Stats")
st.write("ICC rankings and player stats fetched live from the Cricbuzz API.")
st.divider()

# --- Format selector (ODI / Test / T20I) ---
format_choice = st.radio(
    "Select cricket format:",
    options=["ODI", "Test", "T20I"],
    horizontal=True   # shows the radio buttons side by side
)

# Convert to lowercase for the API function
format_map = {"ODI": "odi", "Test": "test", "T20I": "t20i"}
selected_format = format_map[format_choice]

st.divider()

# --- Two columns: Batting and Bowling ---
col_bat, col_bowl = st.columns(2)


# -------------------------------------------------------
# BATTING STATS
# -------------------------------------------------------
with col_bat:
    st.markdown("### 🏏 Top Batsmen")

    if st.button("🔄 Refresh Batsmen", key="refresh_bat"):
        st.rerun()

    with st.spinner("Loading batting stats..."):
        batsmen = get_top_batting_stats(selected_format)

    if batsmen:
        # Save all to database
        if st.button("💾 Save all to DB", key="save_bat"):
            for player in batsmen:
                save_player_to_db(player)
            st.success(f"Saved {len(batsmen)} players to database!")

        # Convert list of dicts to a pandas DataFrame for nice display
        df_bat = pd.DataFrame(batsmen)

        # Rename columns to be more readable
        df_bat = df_bat.rename(columns={
            "rank":    "Rank",
            "name":    "Player",
            "country": "Country",
            "rating":  "Rating"
        })

        # Drop the player_id column (not useful to display)
        df_bat = df_bat.drop(columns=["player_id"], errors="ignore")

        # Display as a table
        st.dataframe(
            df_bat,
            use_container_width=True,   # fills the column width
            hide_index=True             # hides the default 0,1,2 index
        )

        # Show top 3 as a bar chart
        st.markdown("#### Rating comparison (Top 10)")
        chart_data = df_bat.head(10).set_index("Player")["Rating"]
        st.bar_chart(chart_data)

    else:
        st.warning("Could not load batting stats. Check your API key.")


# -------------------------------------------------------
# BOWLING STATS
# -------------------------------------------------------
with col_bowl:
    st.markdown("### 🎳 Top Bowlers")

    if st.button("🔄 Refresh Bowlers", key="refresh_bowl"):
        st.rerun()

    with st.spinner("Loading bowling stats..."):
        bowlers = get_top_bowling_stats(selected_format)

    if bowlers:
        if st.button("💾 Save all to DB", key="save_bowl"):
            for player in bowlers:
                save_player_to_db(player)
            st.success(f"Saved {len(bowlers)} players to database!")

        df_bowl = pd.DataFrame(bowlers)
        df_bowl = df_bowl.rename(columns={
            "rank":    "Rank",
            "name":    "Player",
            "country": "Country",
            "rating":  "Rating"
        })
        df_bowl = df_bowl.drop(columns=["player_id"], errors="ignore")

        st.dataframe(df_bowl, use_container_width=True, hide_index=True)

        st.markdown("#### Rating comparison (Top 10)")
        chart_data = df_bowl.head(10).set_index("Player")["Rating"]
        st.bar_chart(chart_data)

    else:
        st.warning("Could not load bowling stats. Check your API key.")


st.divider()

# --- Summary stats from the DB ---
st.markdown("### 🗄️ Players in your Database")

from utils.db_connection import run_query

db_players = run_query("SELECT full_name, country, playing_role FROM players ORDER BY country")

if db_players:
    df_db = pd.DataFrame(db_players, columns=["Name", "Country", "Role"])
    st.dataframe(df_db, use_container_width=True, hide_index=True)
    st.caption(f"Total: {len(db_players)} players stored in your local database")
else:
    st.info("No players in database yet. Save some from the rankings above!")
