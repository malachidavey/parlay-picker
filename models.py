from database import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)
        
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matchups (
        event_id TEXT PRIMARY KEY,
        sport TEXT NOT NULL ,
        league TEXT,
        home_team TEXT NOT NULL,
        away_team TEXT NOT NULL,
        commence_time TEXT NOT NULL,
        home_odds REAL,
        away_odds REAL,
        bookmaker TEXT,
        last_odds_update TEXT DEFAULT CURRENT_TIMESTAMP)

    """)

    # Migration: add odds columns to pre-existing matchups tables that were
    # created before live-odds support. SQLite ignores duplicate-column errors
    # only if we guard them ourselves.
    for column, coltype in (
        ("home_odds", "REAL"),
        ("away_odds", "REAL"),
        ("bookmaker", "TEXT"),
    ):
        try:
            cursor.execute(f"ALTER TABLE matchups ADD COLUMN {column} {coltype}")
        except Exception:
            pass  # column already exists

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matchup_stats (
        stats_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT NOT NULL,
        team_id TEXT NOT NULL,
        recent_form TEXT,
        head_to_head_summary TEXT,
        injury_notes TEXT,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES matchups(event_id) ON DELETE CASCADE,
        UNIQUE (event_id, team_id))

    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parlays (
        parlay_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        combined_odds REAL,
        implied_probability REAL,
        true_probability REAL,
        ev_value REAL,
        ai_explanation TEXT,
        status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'won', 'lost')),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE)

    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS legs (
        leg_id INTEGER PRIMARY KEY AUTOINCREMENT,
        parlay_id INTEGER NOT NULL,
        event_id TEXT NOT NULL,
        bet_type TEXT NOT NULL CHECK (bet_type IN ('h2h', 'spreads', 'totals')),
        selection TEXT NOT NULL,
        odds_at_pick REAL NOT NULL,
        opponent_odds REAL NOT NULL,
        outcome TEXT NOT NULL DEFAULT 'pending' CHECK (outcome IN ('pending', 'won', 'lost')),
        FOREIGN KEY (parlay_id) REFERENCES parlays(parlay_id) ON DELETE CASCADE,
        FOREIGN KEY (event_id) REFERENCES matchups(event_id) ON DELETE CASCADE)

    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")