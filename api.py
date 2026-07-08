import os
import requests
import os
from queries import insert_matchup, add_leg
from dotenv import load_dotenv
import google.generativeai as genai
import json

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
        
        #  SQL writing inside the  querie file
        insert_matchup(
            event_id=event_id, 
            sport=sport, 
            league=league, 
            home_team=home_team, 
            away_team=away_team, 
            commence_time=commence_time
        )

def print_raw_odds(sport_key="basketball_nba"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if len(data) == 0:
        print("No games returned — try a different sport_key or check if season is active.")
        return

    # just print the first event in full detail
    print(data)

def extract_h2h_odds(event, selected_team, preferred_bookmaker="draftkings"):
    # loop through every bookmaker included in this event's data
    for bookmaker in event.get("bookmakers", []):
        # skip any bookmaker that doesn't match the preferred one
        # (different bookmakers may have different odds for the same event)
        if bookmaker["key"] != preferred_bookmaker:
            continue
        
        # loop through this bookmaker's markets to find the head-to-head (h2h) market
        for market in bookmaker.get("markets", []):
            if market["key"] == "h2h":
                picked_odds = None
                opponent_odds = None
                # loop through the outcomes in the h2h market to find the selected team
                for outcome in market.get("outcomes", []):
                    if outcome["name"] == selected_team:
                        picked_odds = outcome["price"]
                    else:
                        opponent_odds = outcome["price"]
                
                return picked_odds, opponent_odds
    
    return None, None

def add_leg_from_api(parlay_id, event, selected_team, bet_type="h2h"):
    picked_odds, opponent_odds = extract_h2h_odds(event, selected_team)
    if picked_odds is None or opponent_odds is None:
        print(f"Could not find odds for {selected_team} in event {event['id']}")
        return
    add_leg(parlay_id, event['id'], bet_type, selected_team, picked_odds, opponent_odds)

#if __name__ == "__main__":
#    print_raw_odds("baseball_mlb")
#if __name__ == "__main__":
#    sync_upcoming_odds("baseball_mlb")
#if __name__ == "__main__":
#    check_connection() 

if __name__ == "__main__":
    test_event = {
        "id": "57172eebee377baa85502b3c14ce8249",
        "bookmakers": [
            {
                "key": "draftkings",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "San Francisco Giants", "price": 104},
                            {"name": "Toronto Blue Jays", "price": -125}
                        ]
                    }
                ]
            }
        ]
    }

    add_leg_from_api(parlay_id=1, event=test_event, selected_team="San Francisco Giants")
    print("Leg added from API data.")

    picked, opponent = extract_h2h_odds(test_event, "San Francisco Giants")
    print(f"Giants picked_odds: {picked}, opponent_odds: {opponent}")
    # expect: picked_odds: 104, opponent_odds: -125

    picked, opponent = extract_h2h_odds(test_event, "Toronto Blue Jays")
    print(f"Blue Jays picked_odds: {picked}, opponent_odds: {opponent}")
    # expect: picked_odds: -125, opponent_odds: 104