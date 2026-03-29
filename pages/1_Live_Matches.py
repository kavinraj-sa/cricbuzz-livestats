# ============================================================
# pages/1_Live_Matches.py  —  Live Match Page
# Shows currently live cricket matches with scores
# ============================================================

import streamlit as st
from utils.api_helper import get_live_matches, get_recent_matches, save_match_to_db

st.set_page_config(page_title="Live Matches", page_icon="🔴", layout="wide")

st.title("🔴 Live Matches")
st.write("Real-time cricket match updates from Cricbuzz API.")
st.divider()

# --- Tabs: Live and Recent ---
tab1, tab2 = st.tabs(["🔴 Live Now", "📋 Recent Matches"])


# -------------------------------------------------------
# TAB 1: LIVE MATCHES
# -------------------------------------------------------
with tab1:
    # Button to refresh data
    if st.button("🔄 Refresh Live Data", key="refresh_live"):
        st.rerun()   # re-runs the whole page to fetch fresh data

    # Fetch live matches from the API
    with st.spinner("Fetching live matches..."):
        live_matches = get_live_matches()

    if live_matches:
        st.success(f"Found **{len(live_matches)}** live match(es)")

        for match in live_matches:
            # Each match gets its own card using st.container()
            with st.container(border=True):
                # Match title row
                col_title, col_status = st.columns([4, 1])
                with col_title:
                    st.markdown(f"### {match['team1']} vs {match['team2']}")
                with col_status:
                    st.markdown("🟢 **LIVE**")

                # Score row — two columns, one per team
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        label=f"🏏 {match['team1']}",
                        value=f"{match['score_team1']}/{match['wkts_team1']}",
                        delta=f"{match['overs_team1']} overs"
                    )

                with col2:
                    st.metric(
                        label=f"🏏 {match['team2']}",
                        value=f"{match['score_team2']}/{match['wkts_team2']}",
                        delta=f"{match['overs_team2']} overs"
                    )

                # Venue info
                st.caption(f"📍 {match['venue']}, {match['city']}")

                # Save to database button
                if st.button(f"💾 Save to DB", key=f"save_{match['match_id']}"):
                    save_match_to_db(match)
                    st.success("Match saved to database!")

    else:
        st.info("""
        😴 No live matches right now.
        
        Cricket matches don't happen 24/7 — check back when a match is scheduled.
        You can still explore **Recent Matches** in the next tab!
        """)


# -------------------------------------------------------
# TAB 2: RECENT MATCHES
# -------------------------------------------------------
with tab2:
    if st.button("🔄 Refresh Recent", key="refresh_recent"):
        st.rerun()

    with st.spinner("Fetching recent matches..."):
        recent_matches = get_recent_matches()

    if recent_matches:
        st.info(f"Showing last **{len(recent_matches)}** completed matches")

        for match in recent_matches:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{match['team1']} vs {match['team2']}**")
                    st.write(f"📝 {match['description']}")

                    if match.get('winner'):
                        st.success(f"🏆 Winner: **{match['winner']}**  |  Margin: {match.get('victory_margin','')} {match.get('victory_type','')}")

                with col2:
                    st.caption(f"📍 {match.get('venue','')}, {match.get('city','')}")
                    st.caption(f"📅 {match.get('match_date','')}")

                    if st.button("💾 Save", key=f"save_recent_{match['match_id']}"):
                        save_match_to_db(match)
                        st.success("Saved!")
    else:
        st.warning("Could not load recent matches. Check your API key in `utils/api_helper.py`.")
