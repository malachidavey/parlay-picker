import { createContext, useContext, useEffect, useReducer } from 'react'

// The bet slip is the only meaningful client state: the legs you're
// assembling before saving them as a parlay. Held in context so any page
// can read/update it, and mirrored to localStorage so a refresh keeps it.

const STORAGE_KEY = 'parlay-picker.slip'
const BetSlipContext = createContext(null)

// a leg is uniquely identified by (eventId, betType, selection)
const legKey = (l) => `${l.eventId}|${l.betType}|${l.selection}`

function reducer(state, action) {
  switch (action.type) {
    case 'add': {
      const key = legKey(action.leg)
      if (state.some((l) => legKey(l) === key)) return state // no dupes
      return [...state, action.leg]
    }
    case 'remove':
      return state.filter((l) => legKey(l) !== action.key)
    case 'clear':
      return []
    default:
      return state
  }
}

function init() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : []
  } catch {
    return []
  }
}

export function BetSlipProvider({ children }) {
  const [legs, dispatch] = useReducer(reducer, undefined, init)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(legs))
  }, [legs])

  const value = {
    legs,
    addLeg: (leg) => dispatch({ type: 'add', leg }),
    removeLeg: (leg) => dispatch({ type: 'remove', key: legKey(leg) }),
    clear: () => dispatch({ type: 'clear' }),
    has: (leg) => legs.some((l) => legKey(l) === legKey(leg)),
    legKey,
  }

  return <BetSlipContext.Provider value={value}>{children}</BetSlipContext.Provider>
}

// convenience hook so pages do: const slip = useBetSlip()
export function useBetSlip() {
  const ctx = useContext(BetSlipContext)
  if (!ctx) throw new Error('useBetSlip must be used inside <BetSlipProvider>')
  return ctx
}
