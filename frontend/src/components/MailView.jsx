import { useState } from 'react'
import api from '../api'

export default function MailView({ email, onDelete, onReply }) {
  const [password, setPassword] = useState('')
  const [decryptedBody, setDecryptedBody] = useState(null)
  const [verified, setVerified] = useState(false)
  const [decrypting, setDecrypting] = useState(false)
  const [error, setError] = useState('')

  const formatDate = (str) => (str ? new Date(str).toLocaleString() : '')

  const handleDecrypt = async (e) => {
    e.preventDefault()
    setError('')
    setDecrypting(true)
    try {
      const res = await api.post(`/mail/${email.id}/decrypt`, { password })
      setDecryptedBody(res.data.body)
      setVerified(res.data.verified)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to decrypt')
    } finally {
      setDecrypting(false)
    }
  }

  return (
    <>
      <div className="email-view-header">
        <div className="email-view-subject">{email.subject || '(no subject)'}</div>
        <div className="email-view-meta">
          <div><strong>From:</strong> {email.from_addr}</div>
          <div><strong>To:</strong> {email.to_addr}</div>
          {email.cc_addr && <div><strong>Cc:</strong> {email.cc_addr}</div>}
          <div><strong>Date:</strong> {formatDate(email.date)}</div>
        </div>
      </div>
      <div className="email-view-body">
        {!email.ciphertext ? (
          <p>{email.body_text || '(empty)'}</p>
        ) : decryptedBody ? (
          <>
            <p>{decryptedBody}</p>
            <p>{verified ? 'Signature valid' : 'Signature invalid'}</p>
          </>
        ) : (
          <form onSubmit={handleDecrypt}>
            {error && <div className='error-msg'>{error}</div>}
            <input 
              type="password"
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Enter password to decrypt" 
              required 
            />
            <button type="submit" disabled={decrypting}>
              {decrypting ? 'Decrypting...' : 'Decrypt'}
            </button>
          </form>
        )}
      </div>
      <div className="email-view-actions">
        <button className="btn" onClick={onReply}>Reply</button>
        <button className="btn btn-danger" onClick={() => onDelete(email.id)}>Delete</button>
      </div>
    </>
  )
}
