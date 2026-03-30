# ============================================================
# utils/api_helper.py
# Complete Cricbuzz API helper — covers ALL endpoints
# from the API reference sheet
# ============================================================

import requests
from utils.db_connection import run_command, run_query

# -------------------------------------------------------
# YOUR API KEY — paste your RapidAPI key here
# -------------------------------------------------------
API_KEY  = "9083d39540msh7b6680af06eca46p1e40b9jsnb441a8a11b18"
API_HOST = "cricbuzz-cricket.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key":  API_KEY,
    "x-rapidapi-host": API_HOST
}

BASE_URL = "https://cricbuzz-cricket.p.rapidapi.com"


# ============================================================
# BASE FETCH FUNCTION
# ============================================================
def fetch_from_api(endpoint, params=None):
    url = BASE_URL + endpoint
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print("API Error 403: Invalid API key.")
        elif response.status_code == 429:
            print("API Error 429: Rate limit hit.")
        else:
            print(f"API Error: Status {response.status_code}")
        return None
    except requests.exceptions.Timeout:
        print(f"Timeout: {endpoint}")
        return None
    except requests.exceptions.ConnectionError:
        print("No internet connection.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# ============================================================
# CATEGORY 1: MATCHES
# ============================================================

def get_live_matches():
    data = fetch_from_api("/matches/v1/live")
    if not data:
        return []
    matches = []
    try:
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                series_info = series_match.get("seriesAdWrapper", series_match)
                for match in series_info.get("matches", []):
                    info  = match.get("matchInfo", {})
                    score = match.get("matchScore", {})
                    matches.append({
                        "match_id":    info.get("matchId", ""),
                        "series_name": info.get("seriesName", ""),
                        "description": info.get("matchDesc", ""),
                        "format":      info.get("matchFormat", ""),
                        "team1":       info.get("team1", {}).get("teamName", ""),
                        "team2":       info.get("team2", {}).get("teamName", ""),
                        "status":      info.get("status", "Live"),
                        "state":       info.get("state", ""),
                        "venue":       info.get("venueInfo", {}).get("ground", ""),
                        "city":        info.get("venueInfo", {}).get("city", ""),
                        "score_team1": score.get("team1Score", {}).get("inngs1", {}).get("runs", 0),
                        "wkts_team1":  score.get("team1Score", {}).get("inngs1", {}).get("wickets", 0),
                        "overs_team1": score.get("team1Score", {}).get("inngs1", {}).get("overs", 0),
                        "score_team2": score.get("team2Score", {}).get("inngs1", {}).get("runs", 0),
                        "wkts_team2":  score.get("team2Score", {}).get("inngs1", {}).get("wickets", 0),
                        "overs_team2": score.get("team2Score", {}).get("inngs1", {}).get("overs", 0),
                    })
    except Exception as e:
        print(f"Error parsing live matches: {e}")
    return matches


def get_upcoming_matches():
    data = fetch_from_api("/matches/v1/upcoming")
    if not data:
        return []
    matches = []
    try:
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                series_info = series_match.get("seriesAdWrapper", series_match)
                for match in series_info.get("matches", []):
                    info = match.get("matchInfo", {})
                    matches.append({
                        "match_id":    info.get("matchId", ""),
                        "series_name": info.get("seriesName", ""),
                        "description": info.get("matchDesc", ""),
                        "format":      info.get("matchFormat", ""),
                        "team1":       info.get("team1", {}).get("teamName", ""),
                        "team2":       info.get("team2", {}).get("teamName", ""),
                        "status":      info.get("status", ""),
                        "venue":       info.get("venueInfo", {}).get("ground", ""),
                        "city":        info.get("venueInfo", {}).get("city", ""),
                        "start_date":  info.get("startDate", ""),
                    })
    except Exception as e:
        print(f"Error parsing upcoming: {e}")
    return matches


def get_recent_matches():
    data = fetch_from_api("/matches/v1/recent")
    if not data:
        return []
    matches = []
    try:
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                series_info = series_match.get("seriesAdWrapper", series_match)
                for match in series_info.get("matches", []):
                    info = match.get("matchInfo", {})
                    matches.append({
                        "match_id":       info.get("matchId", ""),
                        "series_name":    info.get("seriesName", ""),
                        "description":    info.get("matchDesc", ""),
                        "format":         info.get("matchFormat", ""),
                        "team1":          info.get("team1", {}).get("teamName", ""),
                        "team2":          info.get("team2", {}).get("teamName", ""),
                        "status":         info.get("status", "Completed"),
                        "winner":         info.get("result", {}).get("winningTeam", ""),
                        "victory_margin": info.get("result", {}).get("winningMargin", ""),
                        "victory_type":   info.get("result", {}).get("winByType", ""),
                        "venue":          info.get("venueInfo", {}).get("ground", ""),
                        "city":           info.get("venueInfo", {}).get("city", ""),
                        "match_date":     info.get("startDate", ""),
                    })
    except Exception as e:
        print(f"Error parsing recent: {e}")
    return matches


def get_match_info(match_id):
    data = fetch_from_api("/matches/get-info", params={"matchId": match_id})
    if not data:
        return {}
    return {
        "match_id":    data.get("matchid", ""),
        "series_name": data.get("seriesname", ""),
        "description": data.get("matchdesc", ""),
        "format":      data.get("matchformat", ""),
        "status":      data.get("status", ""),
        "team1":       data.get("team1", {}).get("teamname", ""),
        "team2":       data.get("team2", {}).get("teamname", ""),
        "venue":       data.get("venueinfo", {}).get("ground", ""),
        "city":        data.get("venueinfo", {}).get("city", ""),
        "country":     data.get("venueinfo", {}).get("country", ""),
        "capacity":    data.get("venueinfo", {}).get("capacity", ""),
        "toss":        data.get("tossstatus", ""),
        "umpire1":     data.get("umpire1", {}).get("name", ""),
        "umpire2":     data.get("umpire2", {}).get("name", ""),
        "referee":     data.get("referee", {}).get("name", ""),
        "start_date":  data.get("startdate", ""),
    }


def get_match_team(match_id):
    data = fetch_from_api("/matches/get-team", params={"matchId": match_id})
    if not data:
        return {"playing_xi": [], "bench": []}
    playing_xi, bench = [], []
    try:
        for group in data.get("player", []):
            for p in group.get("player", []):
                player = {
                    "id":      p.get("id", ""),
                    "name":    p.get("name", ""),
                    "role":    p.get("role", ""),
                    "captain": p.get("captain", False),
                    "keeper":  p.get("keeper", False),
                    "team":    p.get("teamname", ""),
                }
                if group.get("category") == "playing XI":
                    playing_xi.append(player)
                else:
                    bench.append(player)
    except Exception as e:
        print(f"Error parsing match team: {e}")
    return {"playing_xi": playing_xi, "bench": bench}


def get_match_scorecard(match_id):
    data = fetch_from_api("/matches/get-scorecard-v2", params={"matchId": match_id})
    if not data:
        return []
    innings_list = []
    try:
        for innings in data.get("scorecard", []):
            batting, bowling = [], []
            for b in innings.get("batsman", []):
                batting.append({
                    "name":        b.get("name", ""),
                    "runs":        b.get("runs", 0),
                    "balls":       b.get("balls", 0),
                    "fours":       b.get("fours", 0),
                    "sixes":       b.get("sixes", 0),
                    "strike_rate": b.get("strkrate", "0"),
                    "dismissal":   b.get("outdec", "not out"),
                })
            for bw in innings.get("bowler", []):
                bowling.append({
                    "name":    bw.get("name", ""),
                    "overs":   bw.get("overs", "0"),
                    "maidens": bw.get("maidens", 0),
                    "runs":    bw.get("runs", 0),
                    "wickets": bw.get("wickets", 0),
                    "economy": bw.get("economy", "0"),
                })
            innings_list.append({
                "innings_id": innings.get("inningsid", ""),
                "team":       innings.get("batteamname", ""),
                "score":      innings.get("score", 0),
                "wickets":    innings.get("wickets", 0),
                "overs":      innings.get("overs", 0),
                "batting":    batting,
                "bowling":    bowling,
            })
    except Exception as e:
        print(f"Error parsing scorecard: {e}")
    return innings_list


def get_match_overs(match_id):
    data = fetch_from_api("/matches/get-overs", params={"matchId": match_id})
    if not data:
        return []
    overs = []
    try:
        for over in data.get("overseplist", {}).get("oversep", []):
            overs.append({
                "over_num":     over.get("overnum", ""),
                "runs":         over.get("runs", 0),
                "score":        over.get("score", 0),
                "wickets":      over.get("wickets", 0),
                "summary":      over.get("oversummary", ""),
                "batting_team": over.get("battingteamname", ""),
                "batsmen":      over.get("ovrbatnames", []),
                "bowler":       over.get("ovrbowlnames", []),
            })
    except Exception as e:
        print(f"Error parsing overs: {e}")
    return overs


# ============================================================
# CATEGORY 2: SCHEDULES
# ============================================================

def get_schedules():
    data = fetch_from_api("/schedule/v1/international")
    if not data:
        return []
    schedule = []
    try:
        for item in data.get("matchScheduleMap", []):
            wrapper = item.get("scheduleAdWrapper", {})
            date = wrapper.get("date", "")
            for series in wrapper.get("matchScheduleList", []):
                series_name = series.get("seriesName", "")
                for match in series.get("matchInfo", []):
                    schedule.append({
                        "date":        date,
                        "series_name": series_name,
                        "match_id":    match.get("matchId", ""),
                        "description": match.get("matchDesc", ""),
                        "format":      match.get("matchFormat", ""),
                        "team1":       match.get("team1", {}).get("teamName", ""),
                        "team2":       match.get("team2", {}).get("teamName", ""),
                        "venue":       match.get("venueInfo", {}).get("ground", ""),
                        "city":        match.get("venueInfo", {}).get("city", ""),
                        "country":     match.get("venueInfo", {}).get("country", ""),
                        "start_date":  match.get("startDate", ""),
                    })
    except Exception as e:
        print(f"Error parsing schedules: {e}")
    return schedule


# ============================================================
# CATEGORY 3: SERIES
# ============================================================

def get_series_list():
    data = fetch_from_api("/series/v1/international")
    if not data:
        return []
    series_list = []
    try:
        for group in data.get("seriesMapProto", []):
            month = group.get("date", "")
            for s in group.get("series", []):
                series_list.append({
                    "series_id":  s.get("id", ""),
                    "name":       s.get("name", ""),
                    "start_date": s.get("startDt", ""),
                    "end_date":   s.get("endDt", ""),
                    "month":      month,
                })
    except Exception as e:
        print(f"Error parsing series list: {e}")
    return series_list


def get_series_archives():
    data = fetch_from_api("/series/v1/archives")
    if not data:
        return []
    archives = []
    try:
        for group in data.get("seriesMapProto", []):
            year = group.get("date", "")
            for s in group.get("series", []):
                archives.append({
                    "series_id":  s.get("id", ""),
                    "name":       s.get("name", ""),
                    "start_date": s.get("startDt", ""),
                    "end_date":   s.get("endDt", ""),
                    "year":       year,
                })
    except Exception as e:
        print(f"Error parsing archives: {e}")
    return archives


def get_series_matches(series_id):
    data = fetch_from_api("/series/v1/matches", params={"seriesId": series_id})
    if not data:
        return []
    matches = []
    try:
        for item in data.get("matchDetails", []):
            wrapper = item.get("matchDetailsMap", {})
            date_key = wrapper.get("key", "")
            for match in wrapper.get("match", []):
                info  = match.get("matchInfo", {})
                score = match.get("matchScore", {})
                matches.append({
                    "match_id":    info.get("matchId", ""),
                    "series_id":   series_id,
                    "description": info.get("matchDesc", ""),
                    "format":      info.get("matchFormat", ""),
                    "state":       info.get("state", ""),
                    "status":      info.get("status", ""),
                    "team1":       info.get("team1", {}).get("teamName", ""),
                    "team2":       info.get("team2", {}).get("teamName", ""),
                    "venue":       info.get("venueInfo", {}).get("ground", ""),
                    "city":        info.get("venueInfo", {}).get("city", ""),
                    "start_date":  info.get("startDate", ""),
                    "date_label":  date_key,
                    "score_t1":    score.get("team1Score", {}).get("inngs1", {}).get("runs", 0),
                    "wkts_t1":     score.get("team1Score", {}).get("inngs1", {}).get("wickets", 0),
                    "score_t2":    score.get("team2Score", {}).get("inngs1", {}).get("runs", 0),
                    "wkts_t2":     score.get("team2Score", {}).get("inngs1", {}).get("wickets", 0),
                })
    except Exception as e:
        print(f"Error parsing series matches: {e}")
    return matches


def get_series_players(series_id, squad_id):
    data = fetch_from_api("/series/v1/players",
                          params={"seriesId": series_id, "squadId": squad_id})
    if not data:
        return []
    players, category = [], ""
    try:
        for item in data.get("player", []):
            if item.get("isHeader"):
                category = item.get("name", "")
                continue
            players.append({
                "player_id":     item.get("id", ""),
                "name":          item.get("name", ""),
                "role":          item.get("role", ""),
                "captain":       item.get("captain", False),
                "batting_style": item.get("battingStyle", ""),
                "bowling_style": item.get("bowlingStyle", ""),
                "category":      category,
            })
    except Exception as e:
        print(f"Error parsing series players: {e}")
    return players


def get_series_venues(series_id):
    data = fetch_from_api("/series/v1/venues", params={"seriesId": series_id})
    if not data:
        return []
    venues = []
    try:
        for v in data.get("seriesVenue", []):
            venues.append({
                "venue_id": v.get("id", ""),
                "name":     v.get("ground", ""),
                "city":     v.get("city", ""),
                "country":  v.get("country", ""),
            })
    except Exception as e:
        print(f"Error parsing series venues: {e}")
    return venues


def get_series_stats(series_id, stat_type="mostRuns"):
    """
    stat_type options:
      Batting : mostRuns, highestScore, highestAvg, highestSr,
                mostHundreds, mostFifties, mostFours, mostSixes
      Bowling : mostWickets, lowestAvg, bestBowlingInnings,
                mostFiveWickets, lowestEcon, lowestSr
    """
    data = fetch_from_api("/series/v1/stats",
                          params={"seriesId": series_id, "statsType": stat_type})
    if not data:
        return []
    rows = []
    try:
        for key in ["testStatsList", "odiStatsList", "t20StatsList"]:
            stats = data.get(key, {})
            headers = stats.get("headers", [])
            for entry in stats.get("values", []):
                vals = entry.get("values", [])
                if vals:
                    row = {"stat_type": stat_type, "format": key.replace("StatsList","").upper()}
                    for i, header in enumerate(headers):
                        row[header] = vals[i] if i < len(vals) else ""
                    rows.append(row)
    except Exception as e:
        print(f"Error parsing series stats: {e}")
    return rows


# ============================================================
# CATEGORY 4: TEAMS
# ============================================================

def get_teams_list():
    data = fetch_from_api("/teams/v1/international")
    if not data:
        return []
    teams, team_type = [], "Unknown"
    try:
        for item in data.get("list", []):
            if "teamId" not in item:
                team_type = item.get("teamName", "Unknown")
                continue
            teams.append({
                "team_id":   item.get("teamId", ""),
                "name":      item.get("teamName", ""),
                "short":     item.get("teamSName", ""),
                "country":   item.get("countryName", ""),
                "team_type": team_type,
            })
    except Exception as e:
        print(f"Error parsing teams: {e}")
    return teams


def get_team_players(team_id):
    data = fetch_from_api("/teams/v1/players", params={"teamId": team_id})
    if not data:
        return []
    players, category = [], ""
    try:
        for item in data.get("player", []):
            if item.get("isHeader"):
                category = item.get("name", "")
                continue
            players.append({
                "player_id":     item.get("id", ""),
                "name":          item.get("name", ""),
                "role":          item.get("role", ""),
                "batting_style": item.get("battingStyle", ""),
                "bowling_style": item.get("bowlingStyle", ""),
                "category":      category,
            })
    except Exception as e:
        print(f"Error parsing team players: {e}")
    return players


def get_team_results(team_id):
    data = fetch_from_api("/teams/v1/results", params={"teamId": team_id})
    if not data:
        return []
    results = []
    try:
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                series_info = series_match.get("seriesAdWrapper", series_match)
                for match in series_info.get("matches", []):
                    info = match.get("matchInfo", {})
                    results.append({
                        "match_id":    info.get("matchId", ""),
                        "description": info.get("matchDesc", ""),
                        "team1":       info.get("team1", {}).get("teamName", ""),
                        "team2":       info.get("team2", {}).get("teamName", ""),
                        "status":      info.get("status", ""),
                        "venue":       info.get("venueInfo", {}).get("ground", ""),
                    })
    except Exception as e:
        print(f"Error parsing team results: {e}")
    return results


def get_team_schedules(team_id):
    data = fetch_from_api("/teams/v1/schedule", params={"teamId": team_id})
    if not data:
        return []
    schedule = []
    try:
        for type_match in data.get("typeMatches", []):
            for series_match in type_match.get("seriesMatches", []):
                series_info = series_match.get("seriesAdWrapper", series_match)
                for match in series_info.get("matches", []):
                    info = match.get("matchInfo", {})
                    schedule.append({
                        "match_id":    info.get("matchId", ""),
                        "description": info.get("matchDesc", ""),
                        "format":      info.get("matchFormat", ""),
                        "team1":       info.get("team1", {}).get("teamName", ""),
                        "team2":       info.get("team2", {}).get("teamName", ""),
                        "status":      info.get("status", ""),
                        "start_date":  info.get("startDate", ""),
                        "venue":       info.get("venueInfo", {}).get("ground", ""),
                        "city":        info.get("venueInfo", {}).get("city", ""),
                    })
    except Exception as e:
        print(f"Error parsing team schedule: {e}")
    return schedule


# ============================================================
# CATEGORY 5: VENUES
# ============================================================

def get_venue_info(venue_id):
    data = fetch_from_api("/venues/get-info", params={"venueId": venue_id})
    if not data:
        return {}
    v = data.get("venueDetails", data)
    return {
        "venue_id": v.get("id", ""),
        "name":     v.get("ground", ""),
        "city":     v.get("city", ""),
        "country":  v.get("country", ""),
        "capacity": v.get("capacity", ""),
        "timezone": v.get("timezone", ""),
    }


def get_venue_matches(venue_id):
    data = fetch_from_api("/venues/get-matches", params={"venueId": venue_id})
    if not data:
        return []
    matches = []
    try:
        for match in data.get("content", {}).get("matches", []):
            info = match.get("matchInfo", {})
            matches.append({
                "match_id":    info.get("matchId", ""),
                "description": info.get("matchDesc", ""),
                "team1":       info.get("team1", {}).get("teamName", ""),
                "team2":       info.get("team2", {}).get("teamName", ""),
                "status":      info.get("status", ""),
                "start_date":  info.get("startDate", ""),
            })
    except Exception as e:
        print(f"Error parsing venue matches: {e}")
    return matches


# ============================================================
# CATEGORY 6: PLAYERS
# ============================================================

def get_trending_players():
    data = fetch_from_api("/stats/v1/player/trending")
    if not data:
        return []
    players = []
    try:
        for p in data.get("player", []):
            players.append({
                "player_id": p.get("id", ""),
                "name":      p.get("name", ""),
                "team":      p.get("teamName", ""),
                "role":      p.get("role", ""),
            })
    except Exception as e:
        print(f"Error parsing trending players: {e}")
    return players


def get_player_info(player_id):
    data = fetch_from_api("/players/get-info", params={"playerId": player_id})
    if not data:
        return {}
    return {
        "player_id":     data.get("id", ""),
        "name":          data.get("name", ""),
        "country":       data.get("country", ""),
        "dob":           data.get("dob", ""),
        "role":          data.get("role", ""),
        "batting_style": data.get("battingStyle", ""),
        "bowling_style": data.get("bowlingStyle", ""),
        "description":   data.get("description", ""),
    }


def get_player_career(player_id):
    data = fetch_from_api("/players/get-career", params={"playerId": player_id})
    if not data:
        return []
    stats = []
    try:
        for item in data.get("troBat", {}).get("troBatting", []):
            stats.append({
                "player_id":    player_id,
                "type":         "batting",
                "format":       item.get("matchtype", ""),
                "matches":      item.get("matches", 0),
                "runs":         item.get("runs", 0),
                "highest":      item.get("highestScore", 0),
                "average":      item.get("avg", 0),
                "strike_rate":  item.get("strikeRate", 0),
                "centuries":    item.get("hundreds", 0),
                "fifties":      item.get("fifties", 0),
            })
        for item in data.get("troBowl", {}).get("troBowling", []):
            stats.append({
                "player_id":  player_id,
                "type":       "bowling",
                "format":     item.get("matchtype", ""),
                "matches":    item.get("matches", 0),
                "wickets":    item.get("wickets", 0),
                "average":    item.get("avg", 0),
                "economy":    item.get("economy", 0),
                "best":       item.get("bestBowling", ""),
                "five_wkts":  item.get("fiveWickets", 0),
            })
    except Exception as e:
        print(f"Error parsing player career: {e}")
    return stats


def get_player_batting_stats(player_id):
    data = fetch_from_api("/players/get-batting", params={"playerId": player_id})
    if not data:
        return []
    stats = []
    try:
        for item in data.get("batting", {}).get("summary", []):
            stats.append({
                "player_id":   player_id,
                "format":      item.get("matchtype", ""),
                "matches":     item.get("matches", 0),
                "runs":        item.get("runs", 0),
                "average":     item.get("avg", 0),
                "strike_rate": item.get("strikeRate", 0),
                "hundreds":    item.get("hundreds", 0),
                "fifties":     item.get("fifties", 0),
                "highest":     item.get("highestScore", 0),
            })
    except Exception as e:
        print(f"Error parsing batting stats: {e}")
    return stats


def get_player_bowling_stats(player_id):
    data = fetch_from_api("/players/get-bowling", params={"playerId": player_id})
    if not data:
        return []
    stats = []
    try:
        for item in data.get("bowling", {}).get("summary", []):
            stats.append({
                "player_id":   player_id,
                "format":      item.get("matchtype", ""),
                "matches":     item.get("matches", 0),
                "wickets":     item.get("wickets", 0),
                "average":     item.get("avg", 0),
                "economy":     item.get("economy", 0),
                "best":        item.get("bestBowling", ""),
                "five_wkts":   item.get("fiveWickets", 0),
                "strike_rate": item.get("strikeRate", 0),
            })
    except Exception as e:
        print(f"Error parsing bowling stats: {e}")
    return stats


def search_player(name):
    data = fetch_from_api("/players/search", params={"plrN": name})
    if not data:
        return []
    players = []
    try:
        for p in data.get("player", []):
            players.append({
                "player_id": p.get("id", ""),
                "name":      p.get("name", ""),
                "team":      p.get("teamName", ""),
                "role":      p.get("role", ""),
            })
    except Exception as e:
        print(f"Error parsing player search: {e}")
    return players


# ============================================================
# CATEGORY 7: STATS / ICC RANKINGS
# ============================================================

def get_icc_rankings(format_type="odi", category="batsmen"):
    """
    format_type : "test" | "odi" | "t20i"
    category    : "batsmen" | "bowlers" | "allrounders" | "teams"
    """
    format_map = {"test": "1", "odi": "2", "t20i": "3"}
    format_id  = format_map.get(format_type.lower(), "2")
    data = fetch_from_api(f"/stats/v1/rankings/{category}",
                          params={"formatType": format_id})
    if not data:
        return []
    players = []
    try:
        for p in data.get("rank", []):
            players.append({
                "rank":      p.get("rank", ""),
                "name":      p.get("name", ""),
                "country":   p.get("country", ""),
                "rating":    p.get("rating", ""),
                "player_id": p.get("id", ""),
            })
    except Exception as e:
        print(f"Error parsing ICC rankings: {e}")
    return players


def get_top_batting_stats(format_type="odi"):
    """Shortcut — ICC batting rankings."""
    return get_icc_rankings(format_type, "batsmen")


def get_top_bowling_stats(format_type="odi"):
    """Shortcut — ICC bowling rankings."""
    return get_icc_rankings(format_type, "bowlers")


# ============================================================
# DATABASE SAVE FUNCTIONS
# ============================================================

def save_match_to_db(match):
    existing = run_query(
        "SELECT id FROM matches WHERE description = ? AND team1 = ? AND team2 = ?",
        (match.get("description",""), match.get("team1",""), match.get("team2",""))
    )
    if existing:
        return
    run_command("""
        INSERT INTO matches (description, team1, team2, status, winner,
                             victory_margin, victory_type, match_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        match.get("description", ""),
        match.get("team1", ""),
        match.get("team2", ""),
        match.get("status", ""),
        match.get("winner", ""),
        match.get("victory_margin", ""),
        match.get("victory_type", ""),
        match.get("match_date", match.get("start_date", "")),
    ))


def save_player_to_db(player):
    existing = run_query(
        "SELECT id FROM players WHERE full_name = ?",
        (player.get("name",""),)
    )
    if existing:
        return
    run_command("""
        INSERT INTO players (full_name, country, playing_role, batting_style, bowling_style)
        VALUES (?, ?, ?, ?, ?)
    """, (
        player.get("name", ""),
        player.get("country", player.get("team", "")),
        player.get("role", ""),
        player.get("batting_style", ""),
        player.get("bowling_style", ""),
    ))


def save_venue_to_db(venue):
    existing = run_query(
        "SELECT id FROM venues WHERE name = ? AND city = ?",
        (venue.get("name",""), venue.get("city",""))
    )
    if existing:
        return
    run_command("""
        INSERT INTO venues (name, city, country, capacity)
        VALUES (?, ?, ?, ?)
    """, (
        venue.get("name",""),
        venue.get("city",""),
        venue.get("country",""),
        venue.get("capacity", 0) or 0,
    ))


def save_batting_stat_to_db(player_db_id, match_db_id, stat, format_type):
    run_command("""
        INSERT INTO batting_stats
            (player_id, match_id, format, runs_scored, balls_faced,
             fours, sixes, strike_rate, highest_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        player_db_id,
        match_db_id,
        format_type,
        stat.get("runs", 0),
        stat.get("balls", 0),
        stat.get("fours", 0),
        stat.get("sixes", 0),
        float(stat.get("strike_rate", 0) or 0),
        stat.get("runs", 0),
    ))


def save_bowling_stat_to_db(player_db_id, match_db_id, stat, format_type):
    run_command("""
        INSERT INTO bowling_stats
            (player_id, match_id, format, overs_bowled, wickets_taken,
             runs_given, economy_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        player_db_id,
        match_db_id,
        format_type,
        float(stat.get("overs", 0) or 0),
        stat.get("wickets", 0),
        stat.get("runs", 0),
        float(stat.get("economy", 0) or 0),
    ))


def refresh_all_data():
    """Fetch everything and save to DB."""
    print("Fetching live matches...")
    for m in get_live_matches():
        save_match_to_db(m)
    print("Fetching recent matches...")
    for m in get_recent_matches():
        save_match_to_db(m)
    print("Fetching ODI batting rankings...")
    for p in get_top_batting_stats("odi"):
        save_player_to_db(p)
    print("Fetching ODI bowling rankings...")
    for p in get_top_bowling_stats("odi"):
        save_player_to_db(p)
    print("All data refreshed!")


# ============================================================
# QUICK TEST — run: python utils/api_helper.py
# ============================================================
if __name__ == "__main__":
    print("Testing API...\n")

    print("--- Live Matches ---")
    live = get_live_matches()
    if live:
        for m in live[:2]:
            print(f"  {m['team1']} vs {m['team2']} | {m['score_team1']}/{m['wkts_team1']}")
    else:
        print("  No live matches right now.")

    print("\n--- ICC ODI Batting Rankings (Top 5) ---")
    for r in get_top_batting_stats("odi")[:5]:
        print(f"  #{r['rank']}  {r['name']} ({r['country']}) — {r['rating']}")

    print("\n--- Player Search: Virat Kohli ---")
    for p in search_player("Virat Kohli")[:3]:
        print(f"  ID: {p['player_id']}  {p['name']}  {p['team']}")

    print("\n--- Series List (first 3) ---")
    for s in get_series_list()[:3]:
        print(f"  {s['name']} ({s['month']})")