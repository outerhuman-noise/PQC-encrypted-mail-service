import { useState } from 'react'
import api from '../api'

const EMPTY_REGISTER = {
  name: '', email: '', password: '',
  email_password: '',
  smtp_host: '', smtp_port: 587,
  imap_host: '', imap_port: 993,
}

export default function Login({ onLogin }) {
  const [tab, setTab] = useState('login')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [loginForm, setLoginForm] = useState({ email: '', password: '' })
  const [regForm, setRegForm] = useState(EMPTY_REGISTER)

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/auth/login', loginForm)
      localStorage.setItem('token', res.data.access_token)
      const me = await api.get('/auth/me')
      onLogin(me.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/register', {
        ...regForm,
        smtp_port: Number(regForm.smtp_port),
        imap_port: Number(regForm.imap_port),
      })
      const res = await api.post('/auth/login', { email: regForm.email, password: regForm.password })
      localStorage.setItem('token', res.data.access_token)
      const me = await api.get('/auth/me')
      onLogin(me.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const setReg = (field) => (e) => setRegForm({ ...regForm, [field]: e.target.value })

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-title">Mail</div>
        <div className="tab-bar">
          <button className={`tab ${tab === 'login' ? 'active' : ''}`} onClick={() => { setTab('login'); setError('') }}>Sign in</button>
          <button className={`tab ${tab === 'register' ? 'active' : ''}`} onClick={() => { setTab('register'); setError('') }}>Create account</button>
        </div>

        {tab === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={loginForm.email} onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })} required autoFocus />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={loginForm.password} onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })} required />
            </div>
            {error && <div className="error-msg">{error}</div>}
            <button className="submit-btn" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label>Name</label>
              <input value={regForm.name} onChange={setReg('name')} required autoFocus />
            </div>
            <div className="form-group">
              <label>Email address</label>
              <input type="email" value={regForm.email} onChange={setReg('email')} required />
            </div>
            <div className="form-group">
              <label>App password <span style={{ fontWeight: 400, color: '#9ca3af' }}>(used to log in here)</span></label>
              <input type="password" value={regForm.password} onChange={setReg('password')} required />
            </div>

            <div className="section-label">Email server settings</div>
            <div className="form-group">
              <label>Email account password <span style={{ fontWeight: 400, color: '#9ca3af' }}>(for SMTP/IMAP)</span></label>
              <input type="password" value={regForm.email_password} onChange={setReg('email_password')} required />
            </div>
            <div className="form-group">
              <div className="form-row">
                <div>
                  <label>SMTP host</label>
                  <input placeholder="smtp.gmail.com" value={regForm.smtp_host} onChange={setReg('smtp_host')} required />
                </div>
                <div>
                  <label>Port</label>
                  <input type="number" value={regForm.smtp_port} onChange={setReg('smtp_port')} required />
                </div>
              </div>
            </div>
            <div className="form-group">
              <div className="form-row">
                <div>
                  <label>IMAP host</label>
                  <input placeholder="imap.gmail.com" value={regForm.imap_host} onChange={setReg('imap_host')} required />
                </div>
                <div>
                  <label>Port</label>
                  <input type="number" value={regForm.imap_port} onChange={setReg('imap_port')} required />
                </div>
              </div>
            </div>
            {error && <div className="error-msg">{error}</div>}
            <button className="submit-btn" disabled={loading}>{loading ? 'Creating account…' : 'Create account'}</button>
          </form>
        )}
      </div>
    </div>
  )
}
