// lib/format.js
// Formatting helpers for odds, EV, and dates.

/** Convert decimal odds (e.g. 1.91) to American odds (e.g. -110). */
export function decimalToAmerican(decimal) {
  if (decimal >= 2) {
    return Math.round((decimal - 1) * 100);
  }
  return Math.round(-100 / (decimal - 1));
}

/** Format a raw American odds number with a leading sign, e.g. +150 / -110. */
export function americanOdds(odds) {
  const rounded = Math.round(odds);
  return rounded > 0 ? `+${rounded}` : `${rounded}`;
}

/** Format an EV value (e.g. 0.0723) as a signed string, e.g. "+0.07" / "-0.10". */
export function evValue(ev) {
  if (ev === null || ev === undefined) return "—";
  const rounded = ev.toFixed(2);
  return ev > 0 ? `+${rounded}` : rounded;
}

/** Return a CSS class name based on whether EV is positive, negative, or neutral. */
export function evClass(ev) {
  if (ev > 0) return "ev-positive";
  if (ev < 0) return "ev-negative";
  return "ev-neutral";
}

/** Format a probability (0-1) as a percentage string, e.g. 0.523 -> "52.3%". */
export function pct(probability) {
  return `${(probability * 100).toFixed(1)}%`;
}

/** Format an ISO datetime string into a readable local date/time. */
export function formatDateTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}
/** Format an ISO datetime string into a short readable date, e.g. "Jul 10". */
export function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}
