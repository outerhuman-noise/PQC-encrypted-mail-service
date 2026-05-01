import { useCallback, useEffect, useState } from 'react'
import api from '../api'
import Compose from './Compose'
import MailView from './MailView'

const FOLDERS = [
  { key: 'INBOX', label: 'Inbox', icon: '📥' },
  { key: 'SENT', label: 'Sent', icon: '📤' },
]

function formatDate(str) {
  if (!str) return ''
  const d = new Date(str)
  const now = new Date()
  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

export default function Inbox({ user, onLogout }) {
  const [folder, setFolder] = useState('INBOX')
  const [emails, setEmails] = useState([])
  const [selected, setSelected] = useState(null)
  const [composing, setComposing] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [loadingList, setLoadingList] = useState(false)

  const loadEmails = useCallback(async () => {
    setLoadingList(true)
    try {
      const res = await api.get(`/mail/?folder=${folder}`)
      setEmails(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingList(false)
    }
  }, [folder])

  useEffect(() => {
    setSelected(null)
    loadEmails()
  }, [loadEmails])

  const handleSync = async () => {
    setSyncing(true)
    try {
      await api.get(`/mail/sync?folder=${folder}`)
      await loadEmails()
    } catch (err) {
      console.error(err)
    } finally {
      setSyncing(false)
    }
  }

  const handleSelect = async (email) => {
    setSelected(email)
    if (!email.is_read) {
      await api.patch(`/mail/${email.id}/read`)
      setEmails((prev) => prev.map((e) => (e.id === email.id ? { ...e, is_read: true } : e)))
    }
  }

  const handleDelete = async (id) => {
    await api.delete(`/mail/${id}`)
    setEmails((prev) => prev.filter((e) => e.id !== id))
    if (selected?.id === id) setSelected(null)
  }

  const unreadCount = emails.filter((e) => !e.is_read).length

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">Mail</div>
        <button className="compose-btn" onClick={() => setComposing(true)}>+ Compose</button>
        <ul className="folder-list">
          {FOLDERS.map((f) => (
            <li
              key={f.key}
              className={`folder-item ${folder === f.key ? 'active' : ''}`}
              onClick={() => setFolder(f.key)}
            >
              <span>{f.icon}</span>
              {f.label}
              {f.key === 'INBOX' && unreadCount > 0 && (
                <span className="unread-badge">{unreadCount}</span>
              )}
            </li>
          ))}
        </ul>
        <div className="user-info">
          <div className="name">{user.name}</div>
          <div className="email-addr">{user.email}</div>
          <button className="logout-btn" onClick={onLogout}>Sign out</button>
        </div>
      </aside>

      <div className="email-list-panel">
        <div className="panel-header">
          {FOLDERS.find((f) => f.key === folder)?.label}
          <button className="sync-btn" onClick={handleSync} disabled={syncing}>
            {syncing ? 'Syncing…' : '↻ Sync'}
          </button>
        </div>
        <div className="email-list">
          {loadingList ? (
            <div className="loading">Loading…</div>
          ) : emails.length === 0 ? (
            <div className="loading" style={{ padding: '32px 16px', textAlign: 'center' }}>
              No emails.{folder === 'INBOX' ? ' Click Sync to fetch from server.' : ''}
            </div>
          ) : (
            emails.map((email) => (
              <div
                key={email.id}
                className={`email-item${!email.is_read ? ' unread' : ''}${selected?.id === email.id ? ' selected' : ''}`}
                onClick={() => handleSelect(email)}
              >
                <div className="email-from">
                  {folder === 'SENT' ? `To: ${email.to_addr}` : email.from_addr}
                </div>
                <div className="email-subject">{email.subject || '(no subject)'}</div>
                <div className="email-preview">{email.body_text?.slice(0, 80)}</div>
                <div className="email-date">{formatDate(email.date)}</div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="email-content-panel">
        {selected ? (
          <MailView
            email={selected}
            onDelete={handleDelete}
            onReply={() => setComposing({ replyTo: selected })}
          />
        ) : (
          <div className="empty-state">
            <div className="empty-icon">✉️</div>
            <div>Select an email to read</div>
          </div>
        )}
      </div>

      {composing && (
        <Compose
          initialTo={composing.replyTo?.from_addr ?? ''}
          initialSubject={composing.replyTo ? `Re: ${composing.replyTo.subject}` : ''}
          onClose={() => setComposing(false)}
          onSent={() => {
            setComposing(false)
            if (folder === 'SENT') loadEmails()
          }}
        />
      )}
    </div>
  )
}
