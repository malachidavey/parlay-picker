import os
import requests
from dotenv import load_dotenv
# Make sure you import both database functions from queries here!
from queries import insert_matchup, insert_matchup_stats
from google import genai

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
SPORTS_DB_KEY = os.getenv("SPORTS_DB_KEY")

def generate_parlay_explanation(legs_summary, ev_value):
    try:
        client = genai.Client(api_key=AI_API_KEY)
        prompt = f"You are a sports analytics expert. Write a sharp, professional 2-sentence breakdown explaining why this parlay holds long-term value: Picks: {legs_summary}, Edge: {ev_value}%."
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"GenAI Error: {e}")
        return "AI analysis temporarily processing."

# ==========================================
# 2. THE ODDS API WORKER
# ==========================================
def sync_upcoming_odds(sport_key="baseball_mlb"):
    """Fetches live upcoming matches and saves them to the database."""
    print(f"Fetching upcoming lines for {sport_key}...")
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        matchups_data = response.json()
        print(f"Found {len(matchups_data)} upcoming games. Syncing to database...")
        for event in matchups_data:
            insert_matchup(
                event_id=event['id'], 
                sport=event['sport_key'], 
                league=event['sport_title'], 
                home_team=event['home_team'], 
                away_team=event['away_team'], 
                commence_time=event['commence_time']
            )

# ==========================================
# 3. THE SPORTSDB WORKER (Place it right here!)
# ==========================================
def fetch_and_store_teams(league_name="English Premier League"):
    """Queries TheSportsDB and writes the team profiles directly into SQLite."""
    print(f"Fetching team directory from TheSportsDB for: {league_name}...")
    
    url = f"https://www.thesportsdb.com/api/v1/json/{SPORTS_DB_KEY}/search_all_teams.php?l={league_name}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch SportsDB data. Status: {response.status_code}")
        return

    data = response.json()
    teams = data.get("teams", [])
    
    for team in teams:
        team_id = team['idTeam']
        team_name = team['strTeam']
        stadium = team['strStadium']
        
        # Call your newly added function from queries.py
        insert_matchup_stats(
            event_id="SETUP_INIT", 
            team_id=team_id, 
            recent_form=f"Stadium: {stadium}"
        )
        print(f"Saved {team_name} profile to database.")

# ==========================================
# 4. EXECUTION RUNNER
# ==========================================
if __name__ == "__main__":
    print("--- Starting Full Core Pipeline Sync ---")
    
    # 1. Sync live match odds
    sync_upcoming_odds("baseball_mlb")
    
    # 2. Sync team profiles
    fetch_and_store_teams("English Premier League")
    
    print("\n--- Testing Gemini Analysis Generation ---")
    test_picks = "Yankees ML & Mets over 7.5 runs"
    test_edge = "4.2"
    analysis = generate_parlay_explanation(test_picks, test_edge)
    print(f"AI Result:\n{analysis}")