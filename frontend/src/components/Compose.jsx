import { useState } from 'react'
import api from '../api'

export default function Compose({ initialTo = '', initialSubject = '', onClose, onSent }) {
  const [form, setForm] = useState({ to: initialTo, cc: '', subject: initialSubject, body: '' })
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSend = async (e) => {
    e.preventDefault()
    setError('')
    setSending(true)
    try {
      await api.post('/mail/send', form)
      onSent()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="compose-modal">
        <div className="compose-header">
          <span>New message</span>
          <button className="compose-close" onClick={onClose} aria-label="Close">×</button>
        </div>
        <form onSubmit={handleSend} style={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
          <div className="compose-field">
            <label>To</label>
            <input value={form.to} onChange={set('to')} placeholder="recipient@example.com" required autoFocus />
          </div>
          <div className="compose-field">
            <label>Cc</label>
            <input value={form.cc} onChange={set('cc')} placeholder="optional" />
          </div>
          <div className="compose-field">
            <label>Subject</label>
            <input value={form.subject} onChange={set('subject')} placeholder="Subject" required />
          </div>
          <textarea
            className="compose-body"
            value={form.body}
            onChange={set('body')}
            placeholder="Write your message…"
          />
          <div className="compose-footer">
            <span className="error-msg">{error}</span>
            <button className="send-btn" type="submit" disabled={sending}>
              {sending ? 'Sending…' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
