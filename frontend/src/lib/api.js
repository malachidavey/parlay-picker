// Single place that knows how to talk to the FastAPI backend.
// Every page calls these instead of using fetch() directly.

// Small helper: make the request, throw on error, return parsed JSON.
async function req(path, init) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail.detail || `${res.status} ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  // --- matchups ---
  listMatchups(sport, league) {
    const p = new URLSearchParams()
    if (sport) p.set('sport', sport)
    if (league) p.set('league', league)
    const qs = p.toString()
    return req(`/api/matchups${qs ? `?${qs}` : ''}`)
  },

  // returns { matchup, stats: [] }
  getMatchup(eventId) {
    return req(`/api/matchups/${eventId}`)
  },

  // pull live upcoming games + real odds from TheOdds API
  syncMatchups(sport) {
    const qs = sport ? `?sport=${encodeURIComponent(sport)}` : ''
    return req(`/api/matchups/sync${qs}`, { method: 'POST' })
  },

  // refresh live AI team stats (form, H2H, injuries) for a matchup
  refreshStats(eventId) {
    return req(`/api/matchups/${eventId}/refresh-stats`, { method: 'POST' })
  },

  // --- parlays ---
  listParlays(userId) {
    return req(`/api/parlays?userId=${userId}`)
  },

  // returns { parlay, legs: [] }
  getParlay(id) {
    return req(`/api/parlays/${id}`)
  },

  createParlay(userId) {
    return req('/api/parlays', {
      method: 'POST',
      body: JSON.stringify({ userId }),
    })
  },

  // generate + persist an AI explanation for a saved parlay
  explainParlay(id) {
    return req(`/api/parlays/${id}/explain`, { method: 'POST' })
  },

  // leg = { eventId, betType, selection, oddsAtPick, opponentOdds }
  addLeg(parlayId, leg) {
    return req(`/api/parlays/${parlayId}/legs`, {
      method: 'POST',
      body: JSON.stringify(leg),
    })
  },

  settleLeg(legId, outcome) {
    return req(`/api/legs/${legId}`, {
      method: 'PATCH',
      body: JSON.stringify({ outcome }),
    })
  },

  // --- EV preview (no save) ---
  // legs = [{ oddsAtPick, opponentOdds }, ...]
  evPreview(legs) {
    return req('/api/ev/preview', {
      method: 'POST',
      body: JSON.stringify({
        legs: legs.map((l) => ({
          oddsAtPick: l.oddsAtPick,
          opponentOdds: l.opponentOdds,
        })),
      }),
    })
  },

  // --- auth ---
  login(username, password) {
    return req('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },

  register(username, email, password) {
    return req('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    })
  },
}
