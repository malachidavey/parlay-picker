"""Populate the database with a demo user and sample matchups.

Run once after creating the tables so the UI has something to show:
    python3 models.py   # create tables
    python3 seed.py     # add sample data
"""
from models import create_tables
import queries as q


def seed():
    create_tables()

    # demo user — log in with username "jordan_b" (any password for now)
    try:
        q.add_user("jordan_b", "jordan@example.com", "demo")
        print("added user jordan_b")
    except Exception:
        print("user jordan_b already exists, skipping")

    # sample upcoming matchups (insert_matchup upserts, so safe to re-run)
    q.insert_matchup("nba_lal_gsw", "basketball_nba", "NBA",
                     "Los Angeles Lakers", "Golden State Warriors",
                     "2026-07-09T23:30:00Z")
    q.insert_matchup("nfl_kc_buf", "americanfootball_nfl", "NFL",
                     "Kansas City Chiefs", "Buffalo Bills",
                     "2026-07-12T20:25:00Z")

    # team stats for the NBA game
    try:
        q.add_matchup_stats("nba_lal_gsw", "Los Angeles Lakers",
                            "W W L W W", "2-1 vs GSW", "None reported")
        q.add_matchup_stats("nba_lal_gsw", "Golden State Warriors",
                            "L W W L L", "1-2 vs LAL", "Curry questionable (ankle)")
        print("added matchup stats")
    except Exception:
        print("matchup stats already exist, skipping")

    print("Seed complete.")


if __name__ == "__main__":
    seed()
