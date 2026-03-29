# pages/2_live.py
import streamlit as st
from utils.api_helper import get_live_matches      # import your function
from utils.db_connection import create_tables      # import DB setup

# Create tables if they don't exist yet
create_tables()

st.title("🔴 Live Matches")

# Button to refresh data from API
if st.button("Refresh Live Data"):
    st.rerun()

# Fetch live matches from the API
matches = get_live_matches()

if matches:
    for match in matches:
        # st.write() prints text on the page
        st.write(f"**{match['team1']} vs {match['team2']}**")
        st.write(f"Score: {match['score_team1']}/{match['wkts_team1']} ({match['overs_team1']} ov)")
        st.write(f"Venue: {match['venue']}, {match['city']}")
        st.divider()   # draws a line between matches
else:
    st.info("No live matches right now. Try checking back later!")