# PQC Encrypted Mail Service

A web mail prototype for sending encrypted messages between registered users.

The app uses a FastAPI backend, a React/Vite frontend, SQLite for local storage,
JWT-based login sessions, and Open Quantum Safe algorithms through
`liboqs-python`. When a user registers, the backend creates a post-quantum KEM
key pair and signature key pair for that account. Private keys are encrypted
with the user's password before they are stored.

Hosted version: https://pqcmail.duckdns.org/

## What It Does

- Register and sign in with a local app account.
- Generate per-user post-quantum encryption and signing keys.
- Send encrypted messages to other registered users.
- Store sent and received messages in SQLite.
- Decrypt received messages by entering the account password.
- Verify message signatures after decryption.
- Mark messages as read and delete messages.

This is an app-to-app encrypted mail system. It does not connect to external
SMTP or IMAP providers.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite, JWT auth
- Frontend: React 18, Vite, Axios
- Cryptography:
  - KEM: `ML-KEM-768` by default
  - Signature: `ML-DSA-65` by default
  - Message encryption: AES-GCM using the KEM shared secret
  - Private key storage: password-derived AES-GCM encryption
- Runtime packaging: Docker Compose

## Project Structure

```text
backend/
  main.py                  FastAPI app entry point
  auth.py                  JWT creation, password hashing, current-user lookup
  database.py              SQLite database setup
  models.py                SQLAlchemy User, UserKeys, and Email models
  schemas.py               Pydantic request/response models
  routers/
    auth.py                Register, login, and current-user routes
    mail.py                List, send, decrypt, read, and delete mail routes
  crypto/
    pqc.py                 liboqs KEM/signature helpers
    key_storage.py         Password-based private key encryption
    symmetric.py           AES-GCM message encryption
    encoding.py            Base64 helpers

frontend/
  src/
    api.js                 Axios client using Vite proxy routes
    App.jsx                Auth bootstrap
    components/
      Login.jsx            Sign in and registration UI
      Inbox.jsx            Mailbox layout
      Compose.jsx          Send message modal
      MailView.jsx         Message decrypt/read/delete view
```

## Prerequisites

The recommended local setup is Docker because the backend depends on native
Open Quantum Safe libraries.

Install:

- Docker Desktop
- Git

## Run Locally With Docker

1. Clone the repository.

```bash
git clone <repo-url>
cd PQC-encrypted-mail-service-main
```

2. Create a backend environment file.

```bash
cd backend
copy .env.example .env
```

On macOS/Linux:

```bash
cd backend
cp .env.example .env
```

The example file contains:

```env
SECRET_KEY=replace-this-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
KEM_ALG=ML-KEM-768
SIG_ALG=ML-DSA-65
```

Replace `SECRET_KEY` with a long random value before using the app beyond a
local demo.

You can generate a strong `SECRET_KEY` with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

3. Start the app from the repository root.

```bash
docker compose up --build
```

4. Open the frontend.

```text
http://localhost:5173
```

The backend API runs at:

```text
http://localhost:8000
```

FastAPI docs are available at:

```text
http://localhost:8000/docs
```

To stop the app:

```bash
docker compose down
```

## Using The App Locally

1. Create at least two accounts, for example `alice@example.com` and
   `bob@example.com`.
2. Sign in as one user.
3. Compose a message to the other registered user's email address.
4. Enter the sender account password when sending so the app can unlock the
   signing key.
5. Sign in as the receiver.
6. Open the received message and enter the receiver account password to decrypt
   it.

Only users already registered in the app can receive messages.

## Local Data

The backend stores data in a SQLite database at:

```text
backend/mail.db
```

When using Docker Compose, `backend/` is mounted into the backend container, so
the database file is persisted in the project folder.

To reset local data, stop the containers and delete `backend/mail.db`.

## API Routes

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

Mail:

- `GET /mail/?folder=INBOX`
- `GET /mail/?folder=SENT`
- `POST /mail/send`
- `POST /mail/{email_id}/decrypt`
- `GET /mail/{email_id}`
- `PATCH /mail/{email_id}/read`
- `DELETE /mail/{email_id}`

Health check:

- `GET /health`

## Manual Development Notes

Running without Docker is possible, but the backend still needs native liboqs
support available to Python. If `liboqs-python` imports but cannot find the
native shared libraries, the app will fail when generating or using keys.

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/auth`, `/mail`, and `/health` to
`http://localhost:8000`.
