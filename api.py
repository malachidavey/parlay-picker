import requests
import os
from queries import insert_matchup
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
SPORTS_DB_KEY = os.getenv("SPORTS_DB_KEY")

genai.configure(api_key=os.getenv("AI_API_KEY"))

def check_connection():
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={ODDS_API_KEY}"
    
    response = requests.get(url)

    if response.status_code == 200:
        print("Connection successful!")
    else:
        print(f"Connection failed with status code: {response.status_code}")  


def sync_upcoming_odds(sport_key="basketball_nba"):
    print(f"Fetching upcoming lines for {sport_key}...")
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Failed to fetch data. Status: {response.status_code}")
        return

    matchups_data = response.json()
    print(f"Found {len(matchups_data)} upcoming games. Syncing to database...")

    # Loop through each event from the API and map it to the overall db
    for event in matchups_data:
        event_id = event['id']
        sport = event['sport_key']
        league = event['sport_title']
        home_team = event['home_team']
        away_team = event['away_team']
        commence_time = event['commence_time']
        
        #  SQL writing inside the  querie file
        insert_matchup(
            event_id=event_id, 
            sport=sport, 
            league=league, 
            home_team=home_team, 
            away_team=away_team, 
            commence_time=commence_time
        )

if __name__ == "__main__":
    sync_upcoming_odds("baseball_mlb")
if __name__ == "__main__":
    check_connection() 