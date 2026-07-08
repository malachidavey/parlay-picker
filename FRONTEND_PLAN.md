# Parlay Picker — Frontend Plan


## 2. Chosen stack

| Concern | Choice |
|---|---|
| Framework | **Next.js (App Router) + TypeScript** |
| UI style | **Plain semantic HTML in JSX + hand-written CSS** (CSS Modules). No component library, no Tailwind. |
| Data layer | **Next.js API routes** (route handlers) reading/writing the existing `parlay_picker.db` via `better-sqlite3` |
| EV / odds math | Ported from `ev_calculator.py` to a TS module (`lib/ev.ts`), unit-tested against the Python outputs |
| Auth | Session cookie; start with a single seeded user, layer real auth later |

Rationale: keeping the UI as plain HTML+CSS keeps the surface small and
readable; Next.js API routes let us drop the separate Python web server while
reusing the SQLite file that already holds the schema and data.

## 3. Screens (routes)

```
/                      Dashboard — your parlays (pending / won / lost), quick EV summary
/matchups              Browse upcoming matchups; filter by sport/league
/matchups/[eventId]    Matchup detail + stats (recent form, H2H, injuries); add legs
/parlay/build          The bet slip — current legs, live combined odds/EV, save
/parlay/[parlayId]     Saved parlay detail — legs, EV breakdown, AI explanation, settle outcomes
/login  /register      Auth
```

## 4. Component inventory (plain HTML + CSS)

Kept intentionally flat — each is a semantic HTML block with a matching
`.module.css`:

- **Layout / nav** — header with links, active-route highlight, user badge.
- **MatchupCard** — teams, commence time, sport/league tag, "add leg" buttons
  per market (`h2h`, `spreads`, `totals`).
- **BetSlip** — running list of selected legs, remove-leg, combined odds, EV
  readout, "save parlay" button. Persisted in state (see §6).
- **OddsPill** — formats American odds (+150 / -110) consistently.
- **EVBadge** — color-coded EV (positive = good), shows EV value + implied vs.
  true probability.
- **ParlayRow / ParlayList** — dashboard listing with status chips.
- **LegList** — legs within a parlay, each with a `won/lost/pending` control.
- **AIExplanation** — renders the stored `ai_explanation` text block.
- **StatusChip**, **EmptyState**, **FormField** — small shared primitives.

## 5. API contract (Next.js route handlers)

Wraps the existing query functions. Shape:

```
GET    /api/matchups                 list matchups (?sport=&league=)
GET    /api/matchups/:eventId        matchup + matchup_stats
POST   /api/parlays                  create parlay { userId } -> parlayId
GET    /api/parlays?userId=          list a user's parlays
GET    /api/parlays/:id              parlay + legs + computed EV + explanation
POST   /api/parlays/:id/legs         add leg { eventId, betType, selection, oddsAtPick }
PATCH  /api/parlays/:id              update odds/EV/status/explanation
PATCH  /api/legs/:legId              settle a leg { outcome }
POST   /api/auth/login  /register    auth
POST   /api/ev/preview               compute combined odds + EV for a draft slip (no save)
```

`/api/ev/preview` powers the live bet-slip numbers without persisting.

## 6. State management

- **Bet slip** is the only meaningful client state. Hold it in a small React
  context + `useReducer`, persisted to `localStorage` so a refresh doesn't wipe
  an in-progress parlay.
- Everything else is server-fetched per route (server components) — no global
  store needed.

## 7. Data flow for the core loop

1. User opens `/matchups`, picks a game, clicks "add leg" on a market.
2. Leg is added to the bet-slip context (odds captured at pick time).
3. Bet slip calls `POST /api/ev/preview` on change → shows live combined odds +
   EV via `lib/ev.ts`.
4. "Save parlay" → `POST /api/parlays`, then `POST .../legs` per leg, then
   `PATCH .../:id` with computed EV + AI explanation.
5. `/parlay/[id]` shows the saved result; user later settles legs → parlay
   status derives from leg outcomes.

## 8. Styling approach

- One `globals.css` with CSS custom properties: color tokens (incl. a
  positive/negative EV palette), spacing scale, type scale, light/dark via
  `prefers-color-scheme`.
- Per-component `*.module.css`. Mobile-first; the bet slip becomes a bottom
  sheet on narrow screens, a sidebar on wide.
- Accessibility: semantic elements, labeled form controls, focus states, EV
  color never the *only* signal (also show the number/sign).

## 9. Build order (milestones)

1. **Scaffold** — `create-next-app` (TS), `globals.css` tokens, layout + nav,
   `better-sqlite3` connection to `parlay_picker.db`.
2. **EV module** — port `ev_calculator.py` → `lib/ev.ts` + tests matching the
   Python results.
3. **Read path** — `/api/matchups`, matchups list + detail pages (static/
   server-rendered). Seed the DB with sample matchups.
4. **Bet slip** — context/reducer, `MatchupCard` add-leg, `/api/ev/preview`,
   live EV in the slip.
5. **Save + view** — create-parlay endpoints, `/parlay/[id]`, `/` dashboard.
6. **Settle outcomes** — leg/parlay status controls + `PATCH` endpoints.
7. **Auth** — login/register, session, scope parlays to the logged-in user.
8. **AI explanation** — wire the `ai_explanation` field to a generator (server
   route calling the model), render in `AIExplanation`.
9. **Polish** — empty/error/loading states, responsive pass, a11y pass.

