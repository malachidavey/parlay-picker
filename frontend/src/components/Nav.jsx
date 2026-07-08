import { NavLink } from 'react-router-dom'
import { useSession } from '../state/Session'

export function Nav() {
  const { user } = useSession()
  return (
    <nav className="appnav">
      <NavLink to="/" className="brand">◆ Parlay Picker</NavLink>
      <NavLink to="/" end>Dashboard</NavLink>
      <NavLink to="/matchups">Matchups</NavLink>
      <NavLink to="/parlay/build">Build</NavLink>
      <span className="spacer" />
      {user
        ? <span className="badge-user">◐ {user.username}</span>
        : <NavLink to="/login" className="badge-user">Log in</NavLink>}
    </nav>
  )
}
