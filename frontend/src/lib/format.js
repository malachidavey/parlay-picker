// Display helpers shared across the UI.

// The backend stores odds as American (-140, +120). Format with a sign.
export function americanOdds(odds) {
  if (odds === null || odds === undefined) return '—'
  return odds > 0 ? `+${odds}` : `${odds}`
}

// Combined odds come back as a decimal multiplier (e.g. 6.40). Show as American.
export function decimalToAmerican(dec) {
  if (!dec || dec <= 1) return '—'
  return dec >= 2
    ? `+${Math.round((dec - 1) * 100)}`
    : `${Math.round(-100 / (dec - 1))}`
}

export function pct(p) {
  if (p === null || p === undefined) return '—'
  return `${(p * 100).toFixed(1)}%`
}

// EV as a signed 2-decimal number, e.g. +0.21 / -0.08
export function evValue(ev) {
  if (ev === null || ev === undefined) return '—'
  return ev >= 0 ? `+${ev.toFixed(2)}` : ev.toFixed(2)
}

export function evClass(ev) {
  if (ev === null || ev === undefined) return ''
  return ev >= 0 ? 'pos' : 'neg'
}

export function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso.replace(' ', 'T'))
  if (isNaN(d)) return iso
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function formatDateTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d)) return iso
  return d.toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
  })
}
