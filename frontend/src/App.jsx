import { useEffect, useState } from 'react'
import api from './api'
import Inbox from './components/Inbox'
import Login from './components/Login'

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.get('/auth/me')
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  if (loading) return <div className="loading">Loading...</div>
  if (!user) return <Login onLogin={setUser} />
  return (
    <Inbox
      user={user}
      onLogout={() => {
        localStorage.removeItem('token')
        setUser(null)
      }}
    />
  )
}
