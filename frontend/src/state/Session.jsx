import { createContext, useContext, useEffect, useState } from 'react'

// Who is logged in. Minimal for now (single seeded user), stored in
// localStorage so it survives refresh. Swap for real cookies/auth later.

const STORAGE_KEY = 'parlay-picker.user'
const SessionContext = createContext(null)

export function SessionProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })

  useEffect(() => {
    if (user) localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
    else localStorage.removeItem(STORAGE_KEY)
  }, [user])

  const value = {
    user,
    login: (u) => setUser(u),
    logout: () => setUser(null),
  }
  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
}

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) throw new Error('useSession must be used inside <SessionProvider>')
  return ctx
}
