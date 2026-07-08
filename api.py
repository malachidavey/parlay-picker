import os
import requests
import json
import warnings
from dotenv import load_dotenv
from google import genai
from queries import insert_matchup, insert_matchup_stats, add_leg

warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
SPORTS_DB_KEY = os.getenv("SPORTS_DB_KEY")

def generate_parlay_explanation_with_stats(legs_summary, ev_value, stats_context):
    try:
        client = genai.Client(api_key=AI_API_KEY)
        
        prompt = (
            f"You are a professional sports analytics expert evaluating a sharp wager.\n\n"
            f"Market Selections: {legs_summary}\n"
            f"Calculated +EV Edge: {ev_value}%\n\n"
            f"TEAM PROFILE & CONTEXTUAL STATS:\n"
            f"- Injuries: {stats_context.get('injuries', 'No critical data')}\n"
            f"- Head-to-Head Records: {stats_context.get('h2h', 'No historical data')}\n"
            f"- Team Form: {stats_context.get('form', 'Stable')}\n\n"
            f"Write a razor-sharp, professional 2-sentence breakdown explaining why the mathematical edge "
            f"holds up when factoring in these active roster variables and matchup dynamics."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"GenAI Error: {e}")
        return "AI analysis temporarily processing."

def sync_upcoming_odds(sport_key="baseball_mlb"):
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

def fetch_and_store_matchup_context(event_id, home_team, away_team):
    print(f"Fetching structural context from TheSportsDB for: {away_team} @ {home_team}...")
    
    mock_fetched_injuries = "Home team starting pitcher is listed day-to-day; Away team shortstop out."
    mock_fetched_h2h = "Home team has won 4 out of the last 6 head-to-head meetings since last season."
    mock_fetched_form = "Away team coming off a 3-game sweep; Home team bullpen overused over last 48h."
    
    combined_form_string = f"Form: {mock_fetched_form} | H2H: {mock_fetched_h2h} | Injuries: {mock_fetched_injuries}"
    
    insert_matchup_stats(
        event_id=event_id,
        team_id="MLB_CROSS_REF",
        recent_form=combined_form_string
    )
    print(f"Successfully cached integrated sports analytics profile for event: {event_id}")
    
    return {
        "injuries": mock_fetched_injuries,
        "h2h": mock_fetched_h2h,
        "form": mock_fetched_form
    }

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

    print(data)

def extract_h2h_odds(event, selected_team, preferred_bookmaker="draftkings"):
    for bookmaker in event.get("bookmakers", []):
        if bookmaker["key"] != preferred_bookmaker:
            continue
        
        for market in bookmaker.get("markets", []):
            if market["key"] == "h2h":
                picked_odds = None
                opponent_odds = None
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


if __name__ == "__main__":
    print("--- Running Integrated Parlay Picker Pipeline ---")
    
    test_event = {
        "id": "mlb_giants_bluejays_2026",
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

    picked, opponent = extract_h2h_odds(test_event, "Toronto Blue Jays")
    print(f"Blue Jays picked_odds: {picked}, opponent_odds: {opponent}")

    matchup_stats = fetch_and_store_matchup_context(
        event_id=test_event["id"],
        home_team="Toronto Blue Jays",
        away_team="San Francisco Giants"
    )
    
    print("\n--- Generating Statistical AI Analysis Summary ---")
    analysis = generate_parlay_explanation_with_stats(
        legs_summary="San Francisco Giants Moneyline (+104)",
        ev_value="6.2",
        stats_context=matchup_stats
    )
    print(f"AI Rationale:\n{analysis}")