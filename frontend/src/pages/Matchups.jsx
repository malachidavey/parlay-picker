import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { MatchupCard } from '../components/MatchupCard'
import { BetSlip } from '../components/BetSlip'
import { EmptyState } from '../components/primitives'

// Browse upcoming matchups; filter by sport/league. Bet slip on the side.
export function Matchups() {
  const [matchups, setMatchups] = useState(null)
  const [error, setError] = useState(null)
  const [sport, setSport] = useState('')
  const [league, setLeague] = useState('')

  useEffect(() => {
    api.listMatchups().then(setMatchups).catch((e) => setError(e.message))
  }, [])

  // filter options derived from the data
  const sports = useMemo(
    () => [...new Set((matchups ?? []).map((m) => m.sport))],
    [matchups],
  )
  const leagues = useMemo(
    () => [...new Set((matchups ?? []).map((m) => m.league).filter(Boolean))],
    [matchups],
  )

  const filtered = (matchups ?? []).filter((m) =>
    (!sport || m.sport === sport) && (!league || m.league === league),
  )

  return (
    <div className="page split">
      <section>
        <h2 className="section-title">Upcoming matchups</h2>
        <div className="toolbar">
          <select value={sport} onChange={(e) => setSport(e.target.value)}>
            <option value="">Sport: All</option>
            {sports.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={league} onChange={(e) => setLeague(e.target.value)}>
            <option value="">League: All</option>
            {leagues.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>

        {error && <p style={{ color: 'var(--neg)' }}>{error}</p>}
        {matchups === null && <p className="muted">Loading…</p>}
        {matchups && filtered.length === 0 && (
          <EmptyState>No matchups match those filters.</EmptyState>
        )}
        {filtered.map((m) => <MatchupCard key={m.event_id} matchup={m} />)}
      </section>

      <BetSlip />
    </div>
  )
}
