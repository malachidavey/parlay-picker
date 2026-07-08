import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useSession } from '../state/Session'
import { StatusChip, EVBadge, EmptyState } from '../components/primitives'
import { decimalToAmerican, formatDate } from '../lib/format'

// Dashboard — your parlays grouped by status + a quick EV summary.
export function Dashboard() {
  const { user } = useSession()
  const [parlays, setParlays] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!user) return
    api.listParlays(user.userId).then(setParlays).catch((e) => setError(e.message))
  }, [user])

  if (!user) {
    return (
      <div className="page">
        <EmptyState>
          Please <Link to="/login">log in</Link> to see your parlays.
        </EmptyState>
      </div>
    )
  }

  const counts = {
    pending: parlays?.filter((p) => p.status === 'pending').length ?? 0,
    won: parlays?.filter((p) => p.status === 'won').length ?? 0,
    lost: parlays?.filter((p) => p.status === 'lost').length ?? 0,
  }
  const evs = (parlays ?? []).map((p) => p.ev_value).filter((v) => v != null)
  const avgEv = evs.length ? evs.reduce((a, b) => a + b, 0) / evs.length : null

  return (
    <div className="page">
      <div className="kpi-row">
        <div className="kpi"><div className="num">{counts.pending}</div><div className="lbl">Pending</div></div>
        <div className="kpi"><div className="num" style={{ color: 'var(--pos)' }}>{counts.won}</div><div className="lbl">Won</div></div>
        <div className="kpi"><div className="num" style={{ color: 'var(--neg)' }}>{counts.lost}</div><div className="lbl">Lost</div></div>
        <div className="kpi"><div className="num"><EVBadge ev={avgEv} /></div><div className="lbl">Avg EV</div></div>
      </div>

      <h2 className="section-title">Your parlays</h2>
      {error && <p style={{ color: 'var(--neg)' }}>{error}</p>}
      {parlays === null && <p className="muted">Loading…</p>}
      {parlays && parlays.length === 0 && (
        <EmptyState>No parlays yet. <Link to="/matchups">Browse matchups →</Link></EmptyState>
      )}

      {parlays?.map((p) => (
        <Link key={p.parlay_id} to={`/parlay/${p.parlay_id}`} className="card row between" style={{ color: 'inherit' }}>
          <div className="stack">
            <div className="row">
              <strong>Parlay #{p.parlay_id}</strong>
              <StatusChip status={p.status} />
            </div>
            <div className="small muted">created {formatDate(p.created_at)}</div>
          </div>
          <div className="row" style={{ gap: 18 }}>
            <span className="pill-odds">{decimalToAmerican(p.combined_odds)}</span>
            <EVBadge ev={p.ev_value} />
            <span className="btn sm">View →</span>
          </div>
        </Link>
      ))}
    </div>
  )
}
