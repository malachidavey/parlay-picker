import { Link } from 'react-router-dom'
import { useBetSlip } from '../state/BetSlip'
import { OddsPill } from './primitives'
import { formatDateTime } from '../lib/format'

// Live h2h prices come from the-odds-api via /api/matchups/sync and land on
// matchup.home_odds / matchup.away_odds. If a matchup predates a sync (or the
// book didn't quote it), we fall back to a deterministic stub so the
// add-leg → bet-slip → save flow still works end to end.
function demoOdds(matchup) {
  const seed = matchup.event_id.length
  const home = seed % 2 === 0 ? -140 : 120
  const away = home < 0 ? 120 : -140
  return { home, away }
}

function resolveOdds(matchup) {
  const { home_odds, away_odds } = matchup
  if (home_odds != null && away_odds != null) {
    return { home: home_odds, away: away_odds, live: true }
  }
  return { ...demoOdds(matchup), live: false }
}

export function MatchupCard({ matchup }) {
  const slip = useBetSlip()
  const odds = resolveOdds(matchup)
  const label = `${matchup.away_team} @ ${matchup.home_team}`

  const homeLeg = {
    eventId: matchup.event_id, matchupLabel: label, betType: 'h2h',
    selection: matchup.home_team, oddsAtPick: odds.home, opponentOdds: odds.away,
  }
  const awayLeg = {
    eventId: matchup.event_id, matchupLabel: label, betType: 'h2h',
    selection: matchup.away_team, oddsAtPick: odds.away, opponentOdds: odds.home,
  }

  return (
    <div className="card">
      <div className="row between">
        <div><strong>{matchup.away_team}</strong> <span className="muted">@</span> <strong>{matchup.home_team}</strong></div>
        <div className="row">
          {matchup.league && <span className="tag">{matchup.league}</span>}
          <span className="tag">{matchup.sport}</span>
        </div>
      </div>
      <div className="small muted" style={{ margin: '6px 0 10px' }}>
        {formatDateTime(matchup.commence_time)}
        {odds.live
          ? <span className="tag" style={{ marginLeft: 8 }}>live{matchup.bookmaker ? ` · ${matchup.bookmaker}` : ''}</span>
          : <span className="small muted" style={{ marginLeft: 8 }}>demo odds</span>}
      </div>
      <div className="row wrap" style={{ gap: 8 }}>
        <AddLegButton slip={slip} leg={awayLeg} label={`+ ${matchup.away_team} ML`} odds={odds.away} />
        <AddLegButton slip={slip} leg={homeLeg} label={`+ ${matchup.home_team} ML`} odds={odds.home} />
        <Link className="btn sm" to={`/matchups/${matchup.event_id}`}>Stats →</Link>
      </div>
    </div>
  )
}

function AddLegButton({ slip, leg, label, odds }) {
  const added = slip.has(leg)
  return (
    <button
      className="btn add sm"
      disabled={added}
      onClick={() => slip.addLeg(leg)}
    >
      {added ? '✓ added' : label} <OddsPill odds={odds} />
    </button>
  )
}
