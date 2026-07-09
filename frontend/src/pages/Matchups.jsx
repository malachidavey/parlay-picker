import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'
import { MatchupCard } from '../components/MatchupCard'
import { BetSlip } from '../components/BetSlip'
import { EmptyState } from '../components/primitives'

// Browse upcoming matchups; filter by sport/league. Bet slip on the side.
const SYNC_SPORTS = [
  { key: 'baseball_mlb', label: 'MLB' },
  { key: 'basketball_nba', label: 'NBA' },
  { key: 'americanfootball_nfl', label: 'NFL' },
  { key: 'icehockey_nhl', label: 'NHL' },
]

export function Matchups() {
  const [matchups, setMatchups] = useState(null)
  const [error, setError] = useState(null)
  const [sport, setSport] = useState('')
  const [league, setLeague] = useState('')
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState(null)
  const [syncSport, setSyncSport] = useState('baseball_mlb')

  const load = () =>
    api.listMatchups().then(setMatchups).catch((e) => setError(e.message))

  useEffect(() => { load() }, [])

  async function syncLive() {
    setSyncing(true)
    setSyncMsg(null)
    setError(null)
    try {
      const r = await api.syncMatchups(syncSport)
      setSyncMsg(`Synced ${r.synced} live ${SYNC_SPORTS.find((s) => s.key === syncSport)?.label || ''} games.`)
      await load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSyncing(false)
    }
  }

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
        <div className="row between" style={{ marginBottom: 4 }}>
          <h2 className="section-title" style={{ margin: 0 }}>Upcoming matchups</h2>
          <div className="row" style={{ gap: 8 }}>
            <select value={syncSport} onChange={(e) => setSyncSport(e.target.value)}>
              {SYNC_SPORTS.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
            </select>
            <button className="btn sm" disabled={syncing} onClick={syncLive}>
              {syncing ? 'Syncing…' : 'Sync live odds'}
            </button>
          </div>
        </div>
        {syncMsg && <p className="small muted">{syncMsg}</p>}

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
