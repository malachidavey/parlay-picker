"""FastAPI layer over the existing Python data + EV logic.

Reuses queries.py, ev_calculator.py and models.py so the Python code stays the
single source of truth. Extra read-only helpers that queries.py doesn't have yet
live here (list matchups, stats-by-event) to avoid churning that file.
"""
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_connection
from models import create_tables
import queries as q
import ev_calculator as ev

app = FastAPI(title="Parlay Picker API")

# Vite dev server origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- helpers not in queries.py ----------
def list_matchups(sport: Optional[str] = None, league: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM matchups"
    where, params = [], []
    if sport:
        where.append("sport = ?")
        params.append(sport)
    if league:
        where.append("league = ?")
        params.append(league)
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY commence_time ASC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def stats_for_event(event_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM matchup_stats WHERE event_id = ?", (event_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- request models ----------
class LegIn(BaseModel):
    eventId: str
    betType: str
    selection: str
    oddsAtPick: float
    opponentOdds: float


class PreviewLeg(BaseModel):
    oddsAtPick: float
    opponentOdds: float


class PreviewIn(BaseModel):
    legs: list[PreviewLeg]


class ParlayCreate(BaseModel):
    userId: int


class LegOutcome(BaseModel):
    outcome: str


class AuthIn(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


# ---------- matchups ----------
@app.get("/api/matchups")
def get_matchups(sport: Optional[str] = None, league: Optional[str] = None):
    return list_matchups(sport, league)


@app.get("/api/matchups/{event_id}")
def get_matchup_detail(event_id: str):
    m = q.get_matchup(event_id)
    if m is None:
        raise HTTPException(404, "matchup not found")
    return {"matchup": dict(m), "stats": stats_for_event(event_id)}


# ---------- parlays ----------
@app.post("/api/parlays")
def create_parlay(body: ParlayCreate):
    parlay_id = q.add_parlay(body.userId)
    return {"parlayId": parlay_id}


@app.get("/api/parlays")
def list_parlays(userId: int):
    return [dict(p) for p in q.get_parlay_by_user(userId)]


@app.get("/api/parlays/{parlay_id}")
def get_parlay(parlay_id: int):
    p = q.get_parlay_by_parlay_id(parlay_id)
    if p is None:
        raise HTTPException(404, "parlay not found")
    legs = [dict(l) for l in q.get_legs_by_parlay(parlay_id)]
    return {"parlay": dict(p), "legs": legs}


@app.post("/api/parlays/{parlay_id}/legs")
def add_parlay_leg(parlay_id: int, body: LegIn):
    q.add_leg(parlay_id, body.eventId, body.betType, body.selection,
              body.oddsAtPick, body.opponentOdds)
    # recompute + persist EV after each leg change
    result = ev.evaluate_parlay(parlay_id)
    return {"ok": True, "ev": result}


@app.patch("/api/legs/{leg_id}")
def settle_leg(leg_id: int, body: LegOutcome):
    if body.outcome not in ("pending", "won", "lost"):
        raise HTTPException(400, "invalid outcome")
    q.update_leg_outcome(leg_id, body.outcome)
    return {"ok": True}


# ---------- EV preview (no persist) ----------
@app.post("/api/ev/preview")
def ev_preview(body: PreviewIn):
    if not body.legs:
        return {"combined_odds": 1.0, "implied_probability": 1.0,
                "true_probability": 1.0, "ev_value": 0.0}
    picked = [leg.oddsAtPick for leg in body.legs]
    combined_odds = ev.calculate_combined_odds(picked)
    implied = 1.0
    true_prob = 1.0
    for leg in body.legs:
        implied *= ev.calculate_implied_probability(leg.oddsAtPick)
        true_prob *= ev.calculate_true_probability(leg.oddsAtPick, leg.opponentOdds)
    ev_value = ev.calculate_ev(true_prob, combined_odds)
    return {
        "combined_odds": combined_odds,
        "implied_probability": implied,
        "true_probability": true_prob,
        "ev_value": ev_value,
    }


# ---------- auth (minimal; single seeded user for now) ----------
@app.post("/api/auth/register")
def register(body: AuthIn):
    if not body.email:
        raise HTTPException(400, "email required")
    q.add_user(body.username, body.email, body.password)  # TODO real hashing
    user = q.get_user(body.username)
    return {"userId": user["user_id"], "username": user["username"]}


@app.post("/api/auth/login")
def login(body: AuthIn):
    user = q.get_user(body.username)
    if user is None:
        raise HTTPException(401, "invalid credentials")
    return {"userId": user["user_id"], "username": user["username"]}


@app.on_event("startup")
def _startup():
    create_tables()
