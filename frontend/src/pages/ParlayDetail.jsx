import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../lib/api'
import { StatusChip, EVBadge, OddsPill, SummaryRow, ProbRow } from '../components/primitives'
import { decimalToAmerican, formatDate } from '../lib/format'

const OUTCOMES = ['won', 'lost', 'pending']

// Saved parlay detail — legs (with settle controls), EV breakdown, AI text.
export function ParlayDetail() {
  const { parlayId } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const load = useCallback(() => {
    api.getParlay(Number(parlayId)).then(setData).catch((e) => setError(e.message))
  }, [parlayId])

  useEffect(() => { load() }, [load])

  async function settle(legId, outcome) {
    await api.settleLeg(legId, outcome)
    load()
  }

  if (error) return <div className="page"><p style={{ color: 'var(--neg)' }}>{error}</p></div>
  if (!data) return <div className="page"><p className="muted">Loading…</p></div>

  const { parlay, legs } = data

  return (
    <div className="page split">
      <section>
        <div className="row between" style={{ marginBottom: 12 }}>
          <h2 className="row" style={{ gap: 10 }}>
            Parlay #{parlay.parlay_id} <StatusChip status={parlay.status} />
          </h2>
          <span className="small muted">created {formatDate(parlay.created_at)}</span>
        </div>

        {legs.map((leg) => (
          <div key={leg.leg_id} className="card row between">
            <div className="stack">
              <strong>{leg.selection}</strong>
              <span className="small muted">{leg.bet_type} · <OddsPill odds={leg.odds_at_pick} /></span>
            </div>
            <div className="row" style={{ gap: 6 }}>
              {OUTCOMES.map((o) => (
                <button
                  key={o}
                  className={`chip ${o === leg.outcome ? 'active' : ''}`}
                  onClick={() => settle(leg.leg_id, o)}
                >
                  {o === leg.outcome ? `✓ ${o}` : o}
                </button>
              ))}
            </div>
          </div>
        ))}
        <p className="small muted">
          Settle each leg — parlay status derives from leg outcomes.
        </p>
      </section>

      <aside className="stack">
        <div className="betslip">
          <h3>EV breakdown</h3>
          <div className="slip-total stack" style={{ borderTop: 'none', marginTop: 0, paddingTop: 0 }}>
            <SummaryRow label="Combined odds">
              <span className="pill-odds">{decimalToAmerican(parlay.combined_odds)}</span>
            </SummaryRow>
            <ProbRow label="Implied prob" value={parlay.implied_probability} />
            <ProbRow label="True prob" value={parlay.true_probability} />
            <div className="row">
              <span className="muted">Expected value</span>
              <EVBadge ev={parlay.ev_value} />
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="section-title">AI explanation</h2>
          <div className="aiblock">
            {parlay.ai_explanation
              ? parlay.ai_explanation
              : <span className="muted">No explanation generated yet.</span>}
          </div>
        </div>
      </aside>
    </div>
  )
}
