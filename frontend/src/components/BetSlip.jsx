import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useBetSlip } from '../state/BetSlip'
import { useSession } from '../state/Session'
import { api } from '../lib/api'
import { decimalToAmerican } from '../lib/format'
import { OddsPill, EVBadge, SummaryRow, ProbRow } from './primitives'

// The running bet slip: current legs + live combined odds/EV, and "save".
// Sidebar on wide screens (see CSS). EV numbers come from the backend via
// /api/ev/preview so the Python math stays the source of truth.
export function BetSlip() {
  const slip = useBetSlip()
  const { user } = useSession()
  const navigate = useNavigate()
  const [ev, setEv] = useState(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  // recompute preview whenever the legs change
  useEffect(() => {
    if (slip.legs.length === 0) {
      setEv(null)
      return
    }
    let cancelled = false
    api.evPreview(slip.legs)
      .then((r) => { if (!cancelled) setEv(r) })
      .catch(() => { if (!cancelled) setEv(null) })
    return () => { cancelled = true }
  }, [slip.legs])

  async function save() {
    if (!user) { navigate('/login'); return }
    setSaving(true)
    setError(null)
    try {
      const { parlayId } = await api.createParlay(user.userId)
      for (const leg of slip.legs) {
        await api.addLeg(parlayId, leg)
      }
      slip.clear()
      navigate(`/parlay/${parlayId}`)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <aside className="betslip">
      <h3>Bet Slip <span className="muted small">{slip.legs.length} legs</span></h3>

      {slip.legs.length === 0 && (
        <p className="muted small">Add legs from the Matchups page.</p>
      )}

      {slip.legs.map((leg) => (
        <div key={slip.legKey(leg)} className="leg row between">
          <span>{leg.selection} <OddsPill odds={leg.oddsAtPick} /></span>
          <button className="iconx" title="remove" onClick={() => slip.removeLeg(leg)}>✕</button>
        </div>
      ))}

      {slip.legs.length > 0 && (
        <>
          <div className="slip-total stack">
            <SummaryRow label="Combined odds">
              <span className="pill-odds">
                {ev ? decimalToAmerican(ev.combined_odds) : '…'}
              </span>
            </SummaryRow>
            <ProbRow label="Implied prob" value={ev?.implied_probability} />
            <ProbRow label="True prob" value={ev?.true_probability} />
            <div className="row">
              <span className="muted">Expected value</span>
              <EVBadge ev={ev?.ev_value} />
            </div>
          </div>

          {error && <p className="small" style={{ color: 'var(--neg)' }}>{error}</p>}

          <button className="btn primary block" style={{ marginTop: 12 }}
                  disabled={saving} onClick={save}>
            {saving ? 'Saving…' : user ? 'Save parlay →' : 'Log in to save'}
          </button>
          <button className="btn block" style={{ marginTop: 6 }}
                  onClick={() => slip.clear()}>Clear slip</button>
          <p className="small muted" style={{ textAlign: 'center', marginTop: 6 }}>
            live via /api/ev/preview
          </p>
        </>
      )}
    </aside>
  )
}
