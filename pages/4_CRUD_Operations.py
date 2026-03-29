# ============================================================
# pages/4_CRUD_Operations.py  —  CRUD Operations Page
# Create, Read, Update, Delete players and matches
# ============================================================

import streamlit as st
import pandas as pd
from utils.db_connection import run_query, run_command

st.set_page_config(page_title="CRUD Operations", page_icon="🛠️", layout="wide")

st.title("🛠️ CRUD Operations")
st.write("Add, view, update, and delete records in your cricket database.")
st.divider()

# --- Tabs for each operation ---
tab_create, tab_read, tab_update, tab_delete = st.tabs([
    "➕ Create", "👁️ Read", "✏️ Update", "🗑️ Delete"
])


# -------------------------------------------------------
# TAB 1: CREATE — Add new records
# -------------------------------------------------------
with tab_create:
    st.markdown("### ➕ Add a New Record")

    # Sub-tabs: Player or Match
    create_type = st.radio("What do you want to add?", ["Player", "Match", "Venue"], horizontal=True)

    # --- Add Player ---
    if create_type == "Player":
        st.markdown("#### Add a New Player")

        with st.form("add_player_form"):
            col1, col2 = st.columns(2)

            with col1:
                name          = st.text_input("Full Name *", placeholder="e.g. Virat Kohli")
                country       = st.text_input("Country *",   placeholder="e.g. India")
                playing_role  = st.selectbox("Playing Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
                date_of_birth = st.text_input("Date of Birth", placeholder="YYYY-MM-DD")

            with col2:
                batting_style = st.selectbox("Batting Style", [
                    "Right-hand bat", "Left-hand bat"
                ])
                bowling_style = st.selectbox("Bowling Style", [
                    "Right-arm fast", "Right-arm fast-medium", "Right-arm medium",
                    "Right-arm off-break", "Right-arm leg-break",
                    "Left-arm fast", "Left-arm fast-medium", "Left-arm medium",
                    "Left-arm orthodox", "Left-arm chinaman", "None"
                ])

            # st.form_submit_button() — submit button inside the form
            submitted = st.form_submit_button("➕ Add Player", type="primary")

            if submitted:
                if not name or not country:
                    st.error("Name and Country are required!")
                else:
                    success = run_command("""
                        INSERT INTO players (full_name, country, playing_role, batting_style, bowling_style, date_of_birth)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (name, country, playing_role, batting_style, bowling_style, date_of_birth))

                    if success:
                        st.success(f"✅ Player **{name}** added successfully!")
                    else:
                        st.error("Something went wrong. Try again.")

    # --- Add Match ---
    elif create_type == "Match":
        st.markdown("#### Add a New Match")

        # Fetch existing venues for the dropdown
        venues = run_query("SELECT id, name, city FROM venues")
        venue_options = {f"{v['name']}, {v['city']}": v['id'] for v in venues} if venues else {}

        with st.form("add_match_form"):
            col1, col2 = st.columns(2)

            with col1:
                description = st.text_input("Match Description *", placeholder="e.g. 1st ODI")
                team1       = st.text_input("Team 1 *", placeholder="e.g. India")
                team2       = st.text_input("Team 2 *", placeholder="e.g. Australia")
                match_date  = st.text_input("Match Date", placeholder="YYYY-MM-DD")

            with col2:
                status      = st.selectbox("Status", ["Upcoming", "Live", "Completed"])
                toss_winner = st.text_input("Toss Winner", placeholder="e.g. India")
                toss_decision = st.selectbox("Toss Decision", ["bat", "bowl"])
                if venue_options:
                    venue_label = st.selectbox("Venue", list(venue_options.keys()))
                    venue_id    = venue_options[venue_label]
                else:
                    st.info("No venues in DB yet. Add one first!")
                    venue_id = None

            submitted = st.form_submit_button("➕ Add Match", type="primary")

            if submitted:
                if not team1 or not team2 or not description:
                    st.error("Description, Team 1, and Team 2 are required!")
                else:
                    success = run_command("""
                        INSERT INTO matches (description, team1, team2, match_date, status, venue_id, toss_winner, toss_decision)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (description, team1, team2, match_date, status, venue_id, toss_winner, toss_decision))

                    if success:
                        st.success(f"✅ Match **{description}** added!")
                    else:
                        st.error("Something went wrong.")

    # --- Add Venue ---
    elif create_type == "Venue":
        st.markdown("#### Add a New Venue")

        with st.form("add_venue_form"):
            col1, col2 = st.columns(2)

            with col1:
                vname    = st.text_input("Venue Name *", placeholder="e.g. Wankhede Stadium")
                city     = st.text_input("City *", placeholder="e.g. Mumbai")

            with col2:
                vcountry = st.text_input("Country *", placeholder="e.g. India")
                capacity = st.number_input("Capacity", min_value=0, value=0, step=1000)

            submitted = st.form_submit_button("➕ Add Venue", type="primary")

            if submitted:
                if not vname or not city or not vcountry:
                    st.error("Name, City, and Country are required!")
                else:
                    success = run_command("""
                        INSERT INTO venues (name, city, country, capacity)
                        VALUES (?, ?, ?, ?)
                    """, (vname, city, vcountry, capacity))

                    if success:
                        st.success(f"✅ Venue **{vname}** added!")
                    else:
                        st.error("Something went wrong.")


# -------------------------------------------------------
# TAB 2: READ — View all records
# -------------------------------------------------------
with tab_read:
    st.markdown("### 👁️ View Records")

    read_type = st.radio("What do you want to view?", ["Players", "Matches", "Venues"], horizontal=True, key="read_radio")

    if read_type == "Players":
        players = run_query("SELECT * FROM players ORDER BY full_name")
        if players:
            df = pd.DataFrame([dict(row) for row in players])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(players)} players")
        else:
            st.info("No players yet. Add some in the Create tab!")

    elif read_type == "Matches":
        matches = run_query("SELECT * FROM matches ORDER BY match_date DESC")
        if matches:
            df = pd.DataFrame([dict(row) for row in matches])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(matches)} matches")
        else:
            st.info("No matches yet.")

    elif read_type == "Venues":
        venues = run_query("SELECT * FROM venues ORDER BY name")
        if venues:
            df = pd.DataFrame([dict(row) for row in venues])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(venues)} venues")
        else:
            st.info("No venues yet.")


# -------------------------------------------------------
# TAB 3: UPDATE — Edit existing records
# -------------------------------------------------------
with tab_update:
    st.markdown("### ✏️ Update a Player Record")

    # Load all players for the dropdown
    players = run_query("SELECT id, full_name, country, playing_role, batting_style, bowling_style FROM players")

    if not players:
        st.info("No players in database. Add some first in the Create tab!")
    else:
        # Create a dropdown with player names
        player_options = {p['full_name']: p for p in players}
        selected_name  = st.selectbox("Select a player to edit:", list(player_options.keys()))
        player         = player_options[selected_name]

        # Pre-fill the form with current values
        with st.form("update_player_form"):
            st.markdown(f"Editing: **{player['full_name']}** (ID: {player['id']})")

            col1, col2 = st.columns(2)

            with col1:
                new_name    = st.text_input("Full Name",   value=player['full_name'])
                new_country = st.text_input("Country",     value=player['country'] or "")
                new_role    = st.selectbox("Playing Role",
                    ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"],
                    index=["Batsman", "Bowler", "All-rounder", "Wicket-keeper"].index(player['playing_role'])
                    if player['playing_role'] in ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"] else 0
                )

            with col2:
                bat_styles  = ["Right-hand bat", "Left-hand bat"]
                new_bat     = st.selectbox("Batting Style", bat_styles,
                    index=bat_styles.index(player['batting_style'])
                    if player['batting_style'] in bat_styles else 0
                )
                new_bowl    = st.text_input("Bowling Style", value=player['bowling_style'] or "")

            submitted = st.form_submit_button("💾 Save Changes", type="primary")

            if submitted:
                success = run_command("""
                    UPDATE players
                    SET full_name=?, country=?, playing_role=?, batting_style=?, bowling_style=?
                    WHERE id=?
                """, (new_name, new_country, new_role, new_bat, new_bowl, player['id']))

                if success:
                    st.success(f"✅ **{new_name}** updated successfully!")
                    st.rerun()
                else:
                    st.error("Update failed. Try again.")


# -------------------------------------------------------
# TAB 4: DELETE — Remove records
# -------------------------------------------------------
with tab_delete:
    st.markdown("### 🗑️ Delete a Record")
    st.warning("⚠️ Deletion is permanent and cannot be undone!")

    delete_type = st.radio("What do you want to delete?", ["Player", "Match"], horizontal=True, key="del_radio")

    if delete_type == "Player":
        players = run_query("SELECT id, full_name, country FROM players ORDER BY full_name")

        if not players:
            st.info("No players to delete.")
        else:
            player_options = {f"{p['full_name']} ({p['country']})": p['id'] for p in players}
            selected       = st.selectbox("Select player to delete:", list(player_options.keys()))
            player_id      = player_options[selected]

            # Confirm before deleting — safety checkbox
            confirm = st.checkbox(f"I confirm I want to permanently delete **{selected}**")

            if st.button("🗑️ Delete Player", type="primary", disabled=not confirm):
                success = run_command("DELETE FROM players WHERE id = ?", (player_id,))
                if success:
                    st.success(f"✅ **{selected}** deleted.")
                    st.rerun()
                else:
                    st.error("Delete failed.")

    elif delete_type == "Match":
        matches = run_query("SELECT id, description, team1, team2 FROM matches ORDER BY id DESC")

        if not matches:
            st.info("No matches to delete.")
        else:
            match_options = {f"{m['description']} — {m['team1']} vs {m['team2']}": m['id'] for m in matches}
            selected      = st.selectbox("Select match to delete:", list(match_options.keys()))
            match_id      = match_options[selected]

            confirm = st.checkbox(f"I confirm I want to permanently delete this match")

            if st.button("🗑️ Delete Match", type="primary", disabled=not confirm):
                success = run_command("DELETE FROM matches WHERE id = ?", (match_id,))
                if success:
                    st.success("✅ Match deleted.")
                    st.rerun()
                else:
                    st.error("Delete failed.")
