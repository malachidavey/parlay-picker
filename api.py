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

def extract_home_away_odds(event, preferred_bookmaker="draftkings"):
    """Pull h2h moneyline prices for the home & away team from an odds-api event.

    Uses the preferred bookmaker when present, otherwise falls back to the first
    bookmaker that quotes h2h. Returns (home_odds, away_odds, bookmaker_key) with
    Nones if no h2h market is available.
    """
    bookmakers = event.get("bookmakers", [])
    if not bookmakers:
        return None, None, None

    chosen = next((b for b in bookmakers if b["key"] == preferred_bookmaker), None) \
        or bookmakers[0]

    for market in chosen.get("markets", []):
        if market["key"] != "h2h":
            continue
        home_odds = away_odds = None
        for outcome in market.get("outcomes", []):
            if outcome["name"] == event["home_team"]:
                home_odds = outcome["price"]
            elif outcome["name"] == event["away_team"]:
                away_odds = outcome["price"]
        return home_odds, away_odds, chosen["key"]

    return None, None, chosen["key"]


def sync_upcoming_odds(sport_key="baseball_mlb"):
    """Fetch live upcoming games + h2h prices and upsert them into the DB.

    Returns the number of games synced so the API layer can report it.
    """
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
        print(f"Odds API error {response.status_code}: {response.text[:200]}")
        raise RuntimeError(f"Odds API returned {response.status_code}")

    matchups_data = response.json()
    print(f"Found {len(matchups_data)} upcoming games. Syncing to database...")
    for event in matchups_data:
        home_odds, away_odds, bookmaker = extract_home_away_odds(event)
        insert_matchup(
            event_id=event['id'],
            sport=event['sport_key'],
            league=event['sport_title'],
            home_team=event['home_team'],
            away_team=event['away_team'],
            commence_time=event['commence_time'],
            home_odds=home_odds,
            away_odds=away_odds,
            bookmaker=bookmaker,
        )
    return len(matchups_data)


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

def get_team_stat_overview(team_name, opponent_name):
    try:
        client = genai.Client(api_key=AI_API_KEY)
        
        prompt = (
            f"Perform a live web search for the active sports matchup: {team_name} vs {opponent_name}.\n"
            f"Find the following metrics:\n"
            f"1. The recent form (W-L streak) over the last 5 games for {team_name}.\n"
            f"2. The recent head-to-head tracking record between {team_name} and {opponent_name}.\n"
            f"3. Active injury reports for {team_name}.\n\n"
            f"CRITICAL CONSTRAINT FOR INJURIES:\n"
            f"- Identify ONLY key impact players (e.g., impact starting pitchers, daily everyday starters, or star closers).\n"
            f"- Limit the output string to a MAXIMUM of 2 key injuries.\n"
            f"- If there are no key impact players injured, return 'None critical reported'.\n\n"
            f"Return a strict JSON object matching these keys exactly, without markdown formatting blocks:\n"
            f'{{"recent_form": "5-letter string e.g. W L W W L based on their latest real-world games", '
            f'"h2h": "recent series standing vs {opponent_name} e.g. 2-1 vs LAL or 4-2 vs TOR", '
            f'"injuries": "string listing max 2 key impact player injuries or None critical reported"}}'
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={"tools": [{"google_search": {}}]}
        )
        
        clean_json_text = response.text.strip().replace("```json", "").replace("```", "")
        parsed_stats = json.loads(clean_json_text)
        
        return {
            "team_name": team_name,
            "recent_form": parsed_stats.get("recent_form", "N/A"),
            "h2h": parsed_stats.get("h2h", "N/A"),
            "injuries": parsed_stats.get("injuries", "None reported")
        }
    except Exception as e:
        print(f"Error pulling stats via AI search: {e}")
        return {
            "team_name": team_name,
            "recent_form": "N/A",
            "h2h": "N/A",
            "injuries": "Data Unavailable"
        }

def refresh_matchup_stats(event_id, home_team, away_team):
    """Pull live AI stats for both teams and persist them to matchup_stats.
    Returns the two stat payloads so the API layer can return them immediately."""
    payloads = []
    for team, opponent in ((home_team, away_team), (away_team, home_team)):
        stats = get_team_stat_overview(team, opponent)
        insert_matchup_stats(
            event_id=event_id,
            team_id=team,
            recent_form=stats["recent_form"],
            head_to_head_summary=stats["h2h"],
            injury_notes=stats["injuries"],
        )
        payloads.append(stats)
    return payloads


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

    print("\n--- Testing Fully Dynamic Live Stat Extraction ---")
    # Testing the Giants stats
    giants_stats = get_team_stat_overview("San Francisco Giants", "Toronto Blue Jays")
    print(f"\n{giants_stats['team_name']} Component Payload:")
    print(json.dumps(giants_stats, indent=4))
    
    # Testing the Blue Jays stats
    jays_stats = get_team_stat_overview("Toronto Blue Jays", "San Francisco Giants")
    print(f"\n{jays_stats['team_name']} Component Payload:")
    print(json.dumps(jays_stats, indent=4))
    
    print("\n--- Generating Statistical AI Analysis Summary ---")
    analysis = generate_parlay_explanation_with_stats(
        legs_summary="San Francisco Giants Moneyline (+104)",
        ev_value="6.2",
        stats_context=matchup_stats
    )
    print(f"AI Rationale:\n{analysis}")