import { americanOdds, evValue, evClass, pct } from '../lib/format'

// OddsPill — American odds in a consistent monospace pill.
export function OddsPill({ odds }) {
  return <span className="pill-odds">{americanOdds(odds)}</span>
}

// EVBadge — color-coded EV. Color is NEVER the only signal: the signed
// number is always shown too (accessibility, plan §8).
export function EVBadge({ ev }) {
  return <span className={`ev ${evClass(ev)}`}>EV {evValue(ev)}</span>
}

// StatusChip — pending / won / lost pill.
export function StatusChip({ status }) {
  return <span className={`chip ${status}`}>{status}</span>
}

// Small labeled probability / number row used inside the slip summary.
export function SummaryRow({ label, children }) {
  return (
    <div className="row">
      <span className="muted">{label}</span>
      <span>{children}</span>
    </div>
  )
}

export function ProbRow({ label, value }) {
  return <SummaryRow label={label}>{pct(value)}</SummaryRow>
}

// EmptyState — friendly placeholder when a list is empty.
export function EmptyState({ children }) {
  return <div className="empty">{children}</div>
}
