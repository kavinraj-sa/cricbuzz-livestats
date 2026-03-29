# ============================================================
# utils/api_helper.py
# This file fetches live cricket data from the Cricbuzz API
# and saves it into your SQLite database.
# ============================================================

import requests                          # for making API calls
from utils.db_connection import run_command, run_query  # your DB functions

# -------------------------------------------------------
# YOUR API KEY — get this from rapidapi.com
# Steps:
#   1. Go to https://rapidapi.com/cricketapilive/api/cricbuzz-cricket/
#   2. Sign up for a free account
#   3. Subscribe to the free plan
#   4. Copy your API key from the dashboard
# -------------------------------------------------------
API_KEY  = "9083d39540msh7b6680af06eca46p1e40b9jsnb441a8a11b18"   # <-- paste your key here
API_HOST = "cricbuzz-cricket.p.rapidapi.com"

# These headers are sent with every API request
HEADERS = {
    "x-rapidapi-key":  API_KEY,
    "x-rapidapi-host": API_HOST
}

# Base URL for all Cricbuzz API endpoints
BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"


# -------------------------------------------------------
# HELPER: Make an API request safely
# All API calls go through this one function.
# -------------------------------------------------------
def fetch_from_api(endpoint):
    """
    Calls the Cricbuzz API at the given endpoint.
    Returns the JSON response as a Python dictionary,
    or None if something went wrong.

    endpoint: the path after the base URL
              e.g. "/matches/v1/live"
    """
    url = BASE_URL + endpoint

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)

        # Check if the request was successful (status code 200 = OK)
        if response.status_code == 200:
            return response.json()   # convert JSON text to Python dict

        elif response.status_code == 403:
            print("API Error: Invalid API key. Check your key on RapidAPI.")
            return None

        elif response.status_code == 429:
            print("API Error: Too many requests. You've hit the free plan limit.")
            return None

        else:
            print(f"API Error: Status code {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("API Error: Request timed out. Check your internet connection.")
        return None

    except requests.exceptions.ConnectionError:
        print("API Error: No internet connection.")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# -------------------------------------------------------
# FUNCTION 1: Fetch live matches
# Returns a list of currently live matches.
# -------------------------------------------------------
def get_live_matches():
    """
    Fetches all currently live cricket matches.
    Returns a list of match dictionaries.
    """
    data = fetch_from_api("/matches/v1/live")

    if data is None:
        return []

    matches = []

    try:
        # The API returns matches grouped in "typeMatches"
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                # Sometimes the key is "seriesAdWrapper", sometimes not
                series_info = series_match.get("seriesAdWrapper", series_match)

                for match in series_info.get("matches", []):
                    match_info = match.get("matchInfo", {})
                    match_score = match.get("matchScore", {})

                    # Pull out the details we care about
                    matches.append({
                        "match_id":    match_info.get("matchId", ""),
                        "description": match_info.get("matchDesc", ""),
                        "team1":       match_info.get("team1", {}).get("teamName", ""),
                        "team2":       match_info.get("team2", {}).get("teamName", ""),
                        "status":      match_info.get("state", "Live"),
                        "venue":       match_info.get("venueInfo", {}).get("ground", ""),
                        "city":        match_info.get("venueInfo", {}).get("city", ""),
                        "score_team1": match_score.get("team1Score", {}).get("inngs1", {}).get("runs", 0),
                        "wkts_team1":  match_score.get("team1Score", {}).get("inngs1", {}).get("wickets", 0),
                        "overs_team1": match_score.get("team1Score", {}).get("inngs1", {}).get("overs", 0),
                        "score_team2": match_score.get("team2Score", {}).get("inngs1", {}).get("runs", 0),
                        "wkts_team2":  match_score.get("team2Score", {}).get("inngs1", {}).get("wickets", 0),
                        "overs_team2": match_score.get("team2Score", {}).get("inngs1", {}).get("overs", 0),
                    })

    except Exception as e:
        print(f"Error parsing live matches: {e}")

    return matches


# -------------------------------------------------------
# FUNCTION 2: Fetch recent (completed) matches
# -------------------------------------------------------
def get_recent_matches():
    """
    Fetches recently completed cricket matches.
    Returns a list of match dictionaries.
    """
    data = fetch_from_api("/matches/v1/recent")

    if data is None:
        return []

    matches = []

    try:
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                series_info = series_match.get("seriesAdWrapper", series_match)

                for match in series_info.get("matches", []):
                    match_info = match.get("matchInfo", {})

                    matches.append({
                        "match_id":      match_info.get("matchId", ""),
                        "description":   match_info.get("matchDesc", ""),
                        "team1":         match_info.get("team1", {}).get("teamName", ""),
                        "team2":         match_info.get("team2", {}).get("teamName", ""),
                        "status":        match_info.get("state", "Completed"),
                        "winner":        match_info.get("result", {}).get("winningTeam", ""),
                        "victory_margin":match_info.get("result", {}).get("winningMargin", ""),
                        "victory_type":  match_info.get("result", {}).get("winByType", ""),
                        "venue":         match_info.get("venueInfo", {}).get("ground", ""),
                        "city":          match_info.get("venueInfo", {}).get("city", ""),
                        "match_date":    match_info.get("startDate", ""),
                    })

    except Exception as e:
        print(f"Error parsing recent matches: {e}")

    return matches


# -------------------------------------------------------
# FUNCTION 3: Fetch top batting stats (ODI)
# -------------------------------------------------------
def get_top_batting_stats(format_type="odi"):
    """
    Fetches top batting stats for a given format.
    format_type: "odi", "test", or "t20i"
    Returns a list of player stat dictionaries.
    """
    # Map format names to API values
    format_map = {
        "test": "1",
        "odi":  "2",
        "t20i": "3"
    }
    format_id = format_map.get(format_type.lower(), "2")

    data = fetch_from_api(f"/stats/v1/rankings/batsmen?formatType={format_id}")

    if data is None:
        return []

    players = []

    try:
        for player in data.get("rank", []):
            players.append({
                "rank":        player.get("rank", ""),
                "name":        player.get("name", ""),
                "country":     player.get("country", ""),
                "rating":      player.get("rating", ""),
                "player_id":   player.get("id", ""),
            })

    except Exception as e:
        print(f"Error parsing batting stats: {e}")

    return players


# -------------------------------------------------------
# FUNCTION 4: Fetch top bowling stats
# -------------------------------------------------------
def get_top_bowling_stats(format_type="odi"):
    """
    Fetches top bowling stats for a given format.
    format_type: "odi", "test", or "t20i"
    """
    format_map = {"test": "1", "odi": "2", "t20i": "3"}
    format_id  = format_map.get(format_type.lower(), "2")

    data = fetch_from_api(f"/stats/v1/rankings/bowlers?formatType={format_id}")

    if data is None:
        return []

    players = []

    try:
        for player in data.get("rank", []):
            players.append({
                "rank":      player.get("rank", ""),
                "name":      player.get("name", ""),
                "country":   player.get("country", ""),
                "rating":    player.get("rating", ""),
                "player_id": player.get("id", ""),
            })

    except Exception as e:
        print(f"Error parsing bowling stats: {e}")

    return players


# -------------------------------------------------------
# FUNCTION 5: Save a match to your database
# Call this after fetching matches from the API.
# -------------------------------------------------------
def save_match_to_db(match):
    """
    Saves a single match dictionary into the matches table.
    Skips saving if the match description already exists.
    """
    # Check if this match is already in the database
    existing = run_query(
        "SELECT id FROM matches WHERE description = ?",
        (match.get("description", ""),)
    )

    if existing:
        return  # already saved, skip

    # Insert the match into the database
    run_command("""
        INSERT INTO matches (description, team1, team2, status, winner, victory_margin, victory_type, match_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        match.get("description", ""),
        match.get("team1", ""),
        match.get("team2", ""),
        match.get("status", ""),
        match.get("winner", ""),
        match.get("victory_margin", ""),
        match.get("victory_type", ""),
        match.get("match_date", ""),
    ))


# -------------------------------------------------------
# FUNCTION 6: Save a player to your database
# -------------------------------------------------------
def save_player_to_db(player):
    """
    Saves a single player dictionary into the players table.
    Skips saving if the player already exists.
    """
    existing = run_query(
        "SELECT id FROM players WHERE full_name = ?",
        (player.get("name", ""),)
    )

    if existing:
        return  # already saved, skip

    run_command("""
        INSERT INTO players (full_name, country)
        VALUES (?, ?)
    """, (
        player.get("name", ""),
        player.get("country", ""),
    ))


# -------------------------------------------------------
# FUNCTION 7: Fetch everything and save to DB in one go
# Call this from your Streamlit app to refresh data.
# -------------------------------------------------------
def refresh_all_data():
    """
    Fetches live matches, recent matches, and top players
    from the API and saves them all to the database.
    """
    print("Fetching live matches...")
    live = get_live_matches()
    for match in live:
        save_match_to_db(match)
    print(f"  Saved {len(live)} live matches.")

    print("Fetching recent matches...")
    recent = get_recent_matches()
    for match in recent:
        save_match_to_db(match)
    print(f"  Saved {len(recent)} recent matches.")

    print("Fetching top ODI batsmen...")
    batsmen = get_top_batting_stats("odi")
    for player in batsmen:
        save_player_to_db(player)
    print(f"  Saved {len(batsmen)} players.")

    print("All data refreshed!")


# -------------------------------------------------------
# QUICK TEST — run this file directly to test your API key
# Type: python utils/api_helper.py
# -------------------------------------------------------
if __name__ == "__main__":
    print("Testing API connection...\n")

    live_matches = get_live_matches()

    if live_matches:
        print(f"Found {len(live_matches)} live matches:\n")
        for m in live_matches[:3]:   # show first 3 only
            print(f"  {m['team1']} vs {m['team2']}")
            print(f"  Venue: {m['venue']}, {m['city']}")
            print(f"  Score: {m['score_team1']}/{m['wkts_team1']} ({m['overs_team1']} ov)")
            print()
    else:
        print("No live matches right now (or API key issue).")
        print("Try checking recent matches instead...\n")

        recent = get_recent_matches()
        if recent:
            print(f"Found {len(recent)} recent matches:")
            for m in recent[:3]:
                print(f"  {m['team1']} vs {m['team2']} — Winner: {m['winner']}")
        else:
            print("Could not fetch data. Please check your API key.")