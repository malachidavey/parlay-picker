import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { useSession } from '../state/Session'

// Shared login/register form. `mode` is 'login' or 'register'.
export function Auth({ mode }) {
  const isRegister = mode === 'register'
  const { login } = useSession()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const user = isRegister
        ? await api.register(username, email, password)
        : await api.login(username, password)
      login(user)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-wrap">
      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <div className="brand" style={{ fontSize: 20, fontWeight: 700 }}>◆ Parlay Picker</div>
        <div className="muted small">
          {isRegister ? 'Create an account' : 'Sign in to track your parlays'}
        </div>
      </div>

      <form className="auth-card" onSubmit={submit}>
        <div className="field">
          <label>Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </div>
        {isRegister && (
          <div className="field">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
        )}
        <div className="field">
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>

        {error && <p className="small" style={{ color: 'var(--neg)' }}>{error}</p>}

        <button className="btn primary block" disabled={busy}>
          {busy ? '…' : isRegister ? 'Register' : 'Log in'}
        </button>

        <div className="small muted" style={{ textAlign: 'center', marginTop: 14 }}>
          {isRegister
            ? <>Have an account? <Link to="/login">Log in →</Link></>
            : <>No account? <Link to="/register">Register →</Link></>}
        </div>
      </form>
    </div>
  )
}
