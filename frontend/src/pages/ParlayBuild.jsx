import { Link } from 'react-router-dom'
import { useBetSlip } from '../state/BetSlip'
import { BetSlip } from '../components/BetSlip'
import { OddsPill, EmptyState } from '../components/primitives'

// The bet slip builder — full-page view of current legs + the live slip panel.
export function ParlayBuild() {
  const slip = useBetSlip()

  return (
    <div className="page split">
      <section>
        <h2 className="section-title">Current legs ({slip.legs.length})</h2>

        {slip.legs.length === 0 && (
          <EmptyState>
            Your slip is empty. <Link to="/matchups">Add legs from Matchups →</Link>
          </EmptyState>
        )}

        {slip.legs.map((leg) => (
          <div key={slip.legKey(leg)} className="card row between">
            <div className="stack">
              <strong>{leg.selection}</strong>
              <span className="small muted">{leg.betType} · {leg.matchupLabel}</span>
            </div>
            <div className="row" style={{ gap: 14 }}>
              <OddsPill odds={leg.oddsAtPick} />
              <button className="iconx" title="remove" onClick={() => slip.removeLeg(leg)}>✕</button>
            </div>
          </div>
        ))}

        {slip.legs.length > 0 && (
          <p className="small muted">Add more legs from the Matchups page →</p>
        )}
      </section>

      <BetSlip />
    </div>
  )
}
