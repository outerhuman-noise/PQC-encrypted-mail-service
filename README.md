# PQC Encrypted Mail Service

A web-based email client built with FastAPI and React. Connects to any standard SMTP/IMAP email provider. Post-quantum cryptography support is planned for a future release.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

That's it. Docker handles Python, Node.js, and all dependencies.

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd PQC-encrypted-mail-service
```

### 2. Create the environment file

```bash
copy backend\.env.example backend\.env
```

Open `backend\.env` and fill in the two required values:

```env
SECRET_KEY=        # any long random string, e.g. output of: python -c "import secrets; print(secrets.token_hex(32))"
FERNET_KEY=        # base64 key, e.g. output of: python -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

> **What are these?**
> - `SECRET_KEY` — signs JWT login tokens
> - `FERNET_KEY` — encrypts your email account password before storing it in the database

### 3. Start the application

```bash
docker compose up --build
```

The `--build` flag is only needed the first time (or after changing `requirements.txt` / `package.json`). After that, just:

```bash
docker compose up
```

Open **http://localhost:5173** in your browser.

To stop: press `Ctrl+C`, or run `docker compose down`.

## Creating an account

When registering you will need your email provider's SMTP and IMAP settings. Common providers:

| Provider | SMTP Host | SMTP Port | IMAP Host | IMAP Port |
|---|---|---|---|---|
| Gmail | `smtp.gmail.com` | `587` | `imap.gmail.com` | `993` |
| Outlook / Hotmail | `smtp-mail.outlook.com` | `587` | `outlook.office365.com` | `993` |
| Yahoo | `smtp.mail.yahoo.com` | `587` | `imap.mail.yahoo.com` | `993` |
| iCloud | `smtp.mail.me.com` | `587` | `imap.mail.me.com` | `993` |

**Gmail users:** Google blocks direct password login. You must create an [App Password](https://myaccount.google.com/apppasswords) (requires 2FA to be enabled) and use that as your email account password.

There are two separate passwords on the registration form:
- **App password** — what you use to log in to this web app
- **Email account password** — your actual email credential used for SMTP/IMAP (stored encrypted)

## Features

- Compose and send emails via SMTP
- Sync and read emails via IMAP (click **↻ Sync** to fetch latest)
- Sent folder (tracks emails sent through this app)
- Unread message badge and read/unread state
- Reply and delete

## Project structure

```
backend/          FastAPI application
  main.py         App entry point
  models.py       SQLAlchemy models (User, Email)
  schemas.py      Pydantic request/response schemas
  auth.py         JWT authentication
  email_crypto.py Fernet encryption for stored email passwords
  smtp_service.py Send email via smtplib
  imap_service.py Fetch email via imaplib
  routers/
    auth.py       /auth/register, /auth/login, /auth/me
    mail.py       /mail/ CRUD + /mail/sync + /mail/send

frontend/         React application (Vite)
  src/
    components/
      Login.jsx   Login and registration form
      Inbox.jsx   Main three-pane layout
      MailView.jsx Email detail view
      Compose.jsx Compose modal
```

## API

The backend API is available at **http://localhost:8000**. Interactive docs are at **http://localhost:8000/docs**.
