import asyncio
import email
import imaplib
from email.header import decode_header
from email.utils import parsedate_to_datetime
from functools import partial
from typing import Any


def _decode_str(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def _get_body(msg) -> tuple:
    text, html = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            disp = part.get("Content-Disposition", "")
            if "attachment" in disp:
                continue
            ct = part.get_content_type()
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            charset = part.get_content_charset() or "utf-8"
            if ct == "text/plain" and not text:
                text = payload.decode(charset, errors="replace")
            elif ct == "text/html" and not html:
                html = payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html = decoded
            else:
                text = decoded
    return text, html


def _fetch(imap_host: str, imap_port: int, email_addr: str, password: str,
           folder: str, max_count: int) -> list[dict[str, Any]]:
    results = []
    with imaplib.IMAP4_SSL(imap_host, imap_port) as imap:
        imap.login(email_addr, password)
        imap.select(folder, readonly=True)
        status, data = imap.search(None, "ALL")
        if status != "OK":
            return results

        ids = data[0].split()
        ids = list(reversed(ids[-max_count:] if len(ids) > max_count else ids))

        for uid in ids:
            try:
                status, raw_data = imap.fetch(uid, "(RFC822)")
                if status != "OK" or not raw_data[0]:
                    continue
                msg = email.message_from_bytes(raw_data[0][1])
                body_text, body_html = _get_body(msg)

                date = None
                if msg.get("Date"):
                    try:
                        date = parsedate_to_datetime(msg["Date"])
                    except Exception:
                        pass

                results.append({
                    "uid": uid.decode(),
                    "message_id": msg.get("Message-ID", "").strip(),
                    "subject": _decode_str(msg.get("Subject", "(no subject)")),
                    "from_addr": _decode_str(msg.get("From", "")),
                    "to_addr": _decode_str(msg.get("To", "")),
                    "cc_addr": _decode_str(msg.get("Cc", "")),
                    "body_text": body_text,
                    "body_html": body_html,
                    "date": date,
                    "folder": folder,
                })
            except Exception as exc:
                print(f"Error fetching UID {uid}: {exc}")
    return results


async def fetch_emails(imap_host: str, imap_port: int, email_addr: str, password: str,
                       folder: str = "INBOX", max_count: int = 50) -> list[dict[str, Any]]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, partial(_fetch, imap_host, imap_port, email_addr, password, folder, max_count)
    )
