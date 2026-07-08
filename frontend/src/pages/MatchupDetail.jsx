import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../lib/api'
import { BetSlip } from '../components/BetSlip'
import { MatchupCard } from '../components/MatchupCard'
import { formatDateTime } from '../lib/format'

// Matchup detail + team stats (recent form, H2H, injuries). Add legs here too.
export function MatchupDetail() {
  const { eventId } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getMatchup(eventId).then(setData).catch((e) => setError(e.message))
  }, [eventId])

  if (error) return <div className="page"><p style={{ color: 'var(--neg)' }}>{error}</p></div>
  if (!data) return <div className="page"><p className="muted">Loading…</p></div>

  const { matchup, stats } = data

  return (
    <div className="page split">
      <section>
        <div className="small muted" style={{ marginBottom: 8 }}>
          <Link to="/matchups">← Back to matchups</Link>
        </div>

        <div className="card">
          <div className="row between">
            <h2 style={{ fontSize: 18 }}>{matchup.away_team} @ {matchup.home_team}</h2>
            <div className="row">
              {matchup.league && <span className="tag">{matchup.league}</span>}
              <span className="small muted">{formatDateTime(matchup.commence_time)}</span>
            </div>
          </div>
        </div>

        <h2 className="section-title">Markets — add to slip</h2>
        <MatchupCard matchup={matchup} />

        <h2 className="section-title" style={{ marginTop: 22 }}>Team stats</h2>
        {stats.length === 0 && <p className="muted small">No stats recorded for this matchup yet.</p>}
        <div className="split" style={{ gridTemplateColumns: '1fr 1fr' }}>
          {stats.map((s) => (
            <div key={s.stats_id} className="card stack">
              <strong>{s.team_id}</strong>
              <div className="small"><span className="muted">Recent form: </span>{s.recent_form || '—'}</div>
              <div className="small"><span className="muted">H2H: </span>{s.head_to_head_summary || '—'}</div>
              <div className="small"><span className="muted">Injuries: </span>{s.injury_notes || '—'}</div>
            </div>
          ))}
        </div>
      </section>

      <BetSlip />
    </div>
  )
}
