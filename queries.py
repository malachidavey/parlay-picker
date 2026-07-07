from database import get_connection

# insert new user into database
def add_user(username, email, password_hash):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, email, password_hash)
        VALUES (? , ? , ?)
        """, (username, email, password_hash))

    conn.commit()
    conn.close()
# fetch a user by username
def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE username = ?
        """, (username,))

    user = cursor.fetchone()
    conn.close()
    return user

# insert new matchup into database
def add_matchup(event_id, sport, league, home_team, away_team, commence_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO matchups (event_id, sport, league, home_team, away_team, commence_time)
        VALUES (? , ? , ? , ? , ? , ?)
        """, (event_id, sport, league, home_team, away_team, commence_time))

    conn.commit()
    conn.close()
# fetch matchup by event_id
def get_matchup(event_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM matchups WHERE event_id = ?
        """, (event_id,))

    matchup = cursor.fetchone()
    conn.close()
    return matchup
# insert matchup stats into database
def add_matchup_stats(event_id, team_id, recent_form, head_to_head_summary, injury_notes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO matchup_stats(event_id, team_id, recent_form, head_to_head_summary, injury_notes)
        VALUES (? , ? , ? , ? , ?)
        """, (event_id, team_id, recent_form, head_to_head_summary, injury_notes))
    
    conn.commit()
    conn.close()

# fetch matchup stats by stats_id
def get_matchup_stats(stats_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM matchup_stats WHERE stats_id = ? 
    """, (stats_id,))

    stats = cursor.fetchone()
    conn.close()
    return stats
# insert new parlay made by a user into the database
def add_parlay(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO parlays(user_id) 
        VALUES (?)
        """, (user_id,))
    
    conn.commit()
    parlay_id = cursor.lastrowid
    conn.close()
    return parlay_id
# fetch all parlays by a user
def get_parlay_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM parlays WHERE user_id = ? 
    """, (user_id,))

    parlay = cursor.fetchall()
    conn.close()
    return parlay

# fetch parlay that matches parlay_id
def get_parlay_by_parlay_id(parlay_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM parlays WHERE parlay_id = ? 
    """, (parlay_id,))

    parlay = cursor.fetchone()
    conn.close()
    return parlay

def insert_matchup(event_id, sport, league, home_team, away_team, commence_time):
    """Inserts an upcoming match or updates it if it already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO matchups (event_id, sport, league, home_team, away_team, commence_time)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                commence_time = excluded.commence_time,
                last_odds_update = CURRENT_TIMESTAMP
        """, (event_id, sport, league, home_team, away_team, commence_time))
        conn.commit()
        print(f"Successfully inserted/updated match: {home_team} vs {away_team}")
    except Exception as e:
        print(f"Database error inserting matchup: {e}")
    finally:
        conn.close()

# update parlay odds
def update_parlay_odds(parlay_id, combined_odds, implied_probability, true_probability, ev_value, ai_explanation, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE parlays
    SET combined_odds = ?, 
        implied_probability = ?,
        true_probability = ?,
        ev_value = ?,
        ai_explanation = ?, 
        status = ?
    WHERE parlay_id = ?
    """, (combined_odds, implied_probability, true_probability, ev_value, ai_explanation, status, parlay_id))

    conn.commit()
    conn.close()

# insert new leg into database
def add_leg(parlay_id, event_id, bet_type, selection, odds_at_pick):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO legs(parlay_id, event_id, bet_type, selection, odds_at_pick)
        VALUES (? , ? , ? , ? , ?)
        """, (parlay_id, event_id, bet_type, selection, odds_at_pick))
    
    conn.commit()
    conn.close()

#fetch all legs in a parlay
def get_legs_by_parlay(parlay_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM legs WHERE parlay_id = ?
    """, (parlay_id,))

    legs = cursor.fetchall()
    conn.close()
    return legs

# update leg outcome
def update_leg_outcome(leg_id, outcome):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE legs
        SET outcome = ?
        WHERE leg_id = ?
    """, (outcome, leg_id))

    conn.commit()
    conn.close()


if __name__ == "__main__":

    # create a user
    add_user("testuser", "test@example.com", "fakehash123")
    user = get_user("testuser")
    print("User", dict(user) if user else None )

    # create a parlay for that user
    parlay_id = add_parlay(user["user_id"])
    print("Parlay ID: ", parlay_id)

    # add a matchup and a leg tied to it 
    add_matchup("test_event_001", "basketball", "NBA", "Knicks", "Spurs", "2026-07-10T23:40:00Z")
    add_leg(parlay_id, "test_event_001", "h2h", "Knicks", -110)

    
    legs = get_legs_by_parlay(parlay_id)
    print("Legs: ", [dict(leg) for leg in legs])

    print("Test passed - no crashes")