import asyncio
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from functools import partial


def _send(smtp_host: str, smtp_port: int, sender: str, password: str,
          to: str, cc: str, subject: str, body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(body, "plain"))

    recipients = [a.strip() for a in f"{to},{cc}".split(",") if a.strip()]

    context = ssl.create_default_context()
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as srv:
            srv.login(sender, password)
            srv.sendmail(sender, recipients, msg.as_string())
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as srv:
            srv.ehlo()
            srv.starttls(context=context)
            srv.login(sender, password)
            srv.sendmail(sender, recipients, msg.as_string())


async def send_email(smtp_host: str, smtp_port: int, sender: str, password: str,
                     to: str, cc: str, subject: str, body: str) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, partial(_send, smtp_host, smtp_port, sender, password, to, cc, subject, body))
