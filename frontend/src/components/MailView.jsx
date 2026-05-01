export default function MailView({ email, onDelete, onReply }) {
  const formatDate = (str) => (str ? new Date(str).toLocaleString() : '')

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
        {email.body_text || (email.body_html ? '(HTML email — plain text unavailable)' : '(empty)')}
      </div>
      <div className="email-view-actions">
        <button className="btn" onClick={onReply}>Reply</button>
        <button className="btn btn-danger" onClick={() => onDelete(email.id)}>Delete</button>
      </div>
    </>
  )
}
