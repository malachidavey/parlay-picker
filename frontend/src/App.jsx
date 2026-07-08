import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { SessionProvider } from './state/Session'
import { BetSlipProvider } from './state/BetSlip'
import { Nav } from './components/Nav'
import { Dashboard } from './pages/Dashboard'
import { Matchups } from './pages/Matchups'
import { MatchupDetail } from './pages/MatchupDetail'
import { ParlayBuild } from './pages/ParlayBuild'
import { ParlayDetail } from './pages/ParlayDetail'
import { Auth } from './pages/Auth'

export default function App() {
  return (
    <SessionProvider>
      <BetSlipProvider>
        <BrowserRouter>
          <div className="app">
            <Nav />
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/matchups" element={<Matchups />} />
              <Route path="/matchups/:eventId" element={<MatchupDetail />} />
              <Route path="/parlay/build" element={<ParlayBuild />} />
              <Route path="/parlay/:parlayId" element={<ParlayDetail />} />
              <Route path="/login" element={<Auth mode="login" />} />
              <Route path="/register" element={<Auth mode="register" />} />
            </Routes>
          </div>
        </BrowserRouter>
      </BetSlipProvider>
    </SessionProvider>
  )
}
