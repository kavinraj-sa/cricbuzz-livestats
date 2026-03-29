# ============================================================
# utils/db_connection.py
# This file handles connecting Python to your SQLite database.
# SQLite stores your data in a single file (cricbuzz.db)
# No server setup needed!
# ============================================================

import sqlite3  # sqlite3 comes built-in with Python, no install needed

# Name of your database file. It will be created automatically
# in the same folder when you run the app for the first time.
DATABASE_NAME = "cricbuzz.db"


# -------------------------------------------------------
# FUNCTION 1: Get a connection to the database
# Call this whenever you want to talk to the database.
# -------------------------------------------------------
def get_connection():
    """
    Opens a connection to the SQLite database.
    Returns the connection object.
    """
    try:
        # connect() opens the database file (creates it if it doesn't exist)
        conn = sqlite3.connect(DATABASE_NAME)

        # This line makes results come back as dictionaries
        # so you can use column names like row["player_name"]
        # instead of row[0], row[1], etc.
        conn.row_factory = sqlite3.Row

        return conn

    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


# -------------------------------------------------------
# FUNCTION 2: Run a SELECT query (reading data)
# Use this to fetch data from the database.
# -------------------------------------------------------
def run_query(sql, params=()):
    """
    Runs a SELECT query and returns the results as a list.

    sql    : your SQL query as a string
    params : values to safely insert into the query (optional)
    """
    conn = get_connection()

    if conn is None:
        return []  # return empty list if connection failed

    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)      # run the SQL
        results = cursor.fetchall()      # get all matching rows
        return results

    except sqlite3.Error as e:
        print(f"Query error: {e}")
        return []

    finally:
        conn.close()  # always close the connection when done


# -------------------------------------------------------
# FUNCTION 3: Run INSERT / UPDATE / DELETE queries
# Use this when you want to change data in the database.
# -------------------------------------------------------
def run_command(sql, params=()):
    """
    Runs an INSERT, UPDATE, or DELETE query.
    Returns True if successful, False if something went wrong.

    sql    : your SQL query as a string
    params : values to safely insert into the query (optional)
    """
    conn = get_connection()

    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)  # run the SQL
        conn.commit()                # save the changes permanently
        return True

    except sqlite3.Error as e:
        print(f"Command error: {e}")
        conn.rollback()  # undo any partial changes if something went wrong
        return False

    finally:
        conn.close()


# -------------------------------------------------------
# FUNCTION 4: Create all your database tables
# Run this ONCE when you first set up the project.
# -------------------------------------------------------
def create_tables():
    """
    Creates all the tables needed for the Cricbuzz project.
    Safe to run multiple times — won't delete existing data.
    """
    conn = get_connection()

    if conn is None:
        return

    try:
        cursor = conn.cursor()

        # --- Players table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name       TEXT NOT NULL,
                country         TEXT,
                playing_role    TEXT,   -- Batsman, Bowler, All-rounder, WK
                batting_style   TEXT,   -- Right-hand bat, Left-hand bat
                bowling_style   TEXT,   -- Right-arm fast, Left-arm spin, etc.
                date_of_birth   TEXT,
                created_at      TEXT DEFAULT (datetime('now'))
            )
        """)

        # --- Venues table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                city        TEXT,
                country     TEXT,
                capacity    INTEGER
            )
        """)

        # --- Series table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS series (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                host_country    TEXT,
                match_type      TEXT,   -- Test, ODI, T20I
                start_date      TEXT,
                end_date        TEXT,
                total_matches   INTEGER
            )
        """)

        # --- Matches table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                series_id       INTEGER REFERENCES series(id),
                venue_id        INTEGER REFERENCES venues(id),
                description     TEXT,
                team1           TEXT,
                team2           TEXT,
                match_date      TEXT,
                status          TEXT,   -- Live, Completed, Upcoming
                winner          TEXT,
                victory_margin  TEXT,
                victory_type    TEXT,   -- runs, wickets
                toss_winner     TEXT,
                toss_decision   TEXT    -- bat, bowl
            )
        """)

        # --- Batting stats table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batting_stats (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id       INTEGER REFERENCES players(id),
                match_id        INTEGER REFERENCES matches(id),
                format          TEXT,   -- Test, ODI, T20I
                innings         INTEGER,
                runs_scored     INTEGER DEFAULT 0,
                balls_faced     INTEGER DEFAULT 0,
                fours           INTEGER DEFAULT 0,
                sixes           INTEGER DEFAULT 0,
                strike_rate     REAL DEFAULT 0.0,
                batting_average REAL DEFAULT 0.0,
                centuries       INTEGER DEFAULT 0,
                fifties         INTEGER DEFAULT 0,
                highest_score   INTEGER DEFAULT 0,
                batting_position INTEGER,
                match_year      INTEGER
            )
        """)

        # --- Bowling stats table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bowling_stats (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id       INTEGER REFERENCES players(id),
                match_id        INTEGER REFERENCES matches(id),
                format          TEXT,
                innings         INTEGER,
                overs_bowled    REAL DEFAULT 0.0,
                wickets_taken   INTEGER DEFAULT 0,
                runs_given      INTEGER DEFAULT 0,
                economy_rate    REAL DEFAULT 0.0,
                bowling_average REAL DEFAULT 0.0,
                match_year      INTEGER
            )
        """)

        # --- Fielding stats table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fielding_stats (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id   INTEGER REFERENCES players(id),
                match_id    INTEGER REFERENCES matches(id),
                catches     INTEGER DEFAULT 0,
                stumpings   INTEGER DEFAULT 0,
                run_outs    INTEGER DEFAULT 0
            )
        """)

        conn.commit()
        print("All tables created successfully!")

    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

    finally:
        conn.close()


# -------------------------------------------------------
# FUNCTION 5: Insert sample data for testing
# Useful so you can test queries without real API data.
# -------------------------------------------------------
def insert_sample_data():
    """
    Inserts a few sample rows so you can test your SQL queries.
    """
    # Sample players
    players = [
        ("Virat Kohli",    "India",     "Batsman",     "Right-hand bat", "Right-arm medium", "1988-11-05"),
        ("Rohit Sharma",   "India",     "Batsman",     "Right-hand bat", "Right-arm off-break", "1987-04-30"),
        ("Jasprit Bumrah", "India",     "Bowler",      "Right-hand bat", "Right-arm fast", "1993-12-06"),
        ("Ben Stokes",     "England",   "All-rounder", "Left-hand bat",  "Right-arm fast-medium", "1991-06-04"),
        ("Steve Smith",    "Australia", "Batsman",     "Right-hand bat", "Right-arm leg-break", "1989-06-02"),
    ]
    for p in players:
        run_command(
            "INSERT OR IGNORE INTO players (full_name, country, playing_role, batting_style, bowling_style, date_of_birth) VALUES (?,?,?,?,?,?)",
            p
        )

    # Sample venue
    run_command(
        "INSERT OR IGNORE INTO venues (name, city, country, capacity) VALUES (?,?,?,?)",
        ("Wankhede Stadium", "Mumbai", "India", 33108)
    )

    # Sample series
    run_command(
        "INSERT OR IGNORE INTO series (name, host_country, match_type, start_date, end_date, total_matches) VALUES (?,?,?,?,?,?)",
        ("India vs Australia 2024", "India", "ODI", "2024-09-01", "2024-09-15", 3)
    )

    print("Sample data inserted!")


# -------------------------------------------------------
# QUICK TEST — runs only when you execute this file directly
# Type: python db_connection.py
# -------------------------------------------------------
if __name__ == "__main__":
    print("Setting up database...")
    create_tables()
    insert_sample_data()

    # Test: fetch all players
    players = run_query("SELECT full_name, country, playing_role FROM players")
    print("\nPlayers in database:")
    for row in players:
        print(f"  {row['full_name']} — {row['country']} — {row['playing_role']}")