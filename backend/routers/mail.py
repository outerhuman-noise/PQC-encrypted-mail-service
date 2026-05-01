from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from database import get_db
from email_crypto import decrypt_password
from imap_service import fetch_emails
from smtp_service import send_email

router = APIRouter(prefix="/mail", tags=["mail"])


async def _sync_folder(user: models.User, folder: str, db: Session) -> int:
    password = decrypt_password(user.encrypted_email_password)
    fetched = await fetch_emails(user.imap_host, user.imap_port, user.email, password, folder)

    new_count = 0
    for item in fetched:
        if not item["message_id"]:
            continue
        exists = db.query(models.Email).filter(
            models.Email.user_id == user.id,
            models.Email.message_id == item["message_id"],
            models.Email.folder == folder,
        ).first()
        if not exists:
            db.add(models.Email(
                user_id=user.id,
                message_id=item["message_id"],
                uid=item["uid"],
                subject=item["subject"],
                from_addr=item["from_addr"],
                to_addr=item["to_addr"],
                cc_addr=item["cc_addr"],
                body_text=item["body_text"],
                body_html=item["body_html"],
                date=item["date"],
                folder=folder,
            ))
            new_count += 1

    db.commit()
    return new_count


@router.get("/sync")
async def sync(
    folder: str = "INBOX",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.imap_host:
        raise HTTPException(status_code=400, detail="IMAP not configured")
    try:
        new_count = await _sync_folder(current_user, folder, db)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"IMAP error: {exc}")
    return {"status": "synced", "new": new_count}


@router.get("/", response_model=List[schemas.EmailResponse])
def list_emails(
    folder: str = "INBOX",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Email)
        .filter(models.Email.user_id == current_user.id, models.Email.folder == folder)
        .order_by(models.Email.date.desc().nullslast())
        .all()
    )


@router.post("/send")
async def send_mail(
    data: schemas.SendEmailRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.smtp_host:
        raise HTTPException(status_code=400, detail="SMTP not configured")

    password = decrypt_password(current_user.encrypted_email_password)
    try:
        await send_email(
            smtp_host=current_user.smtp_host,
            smtp_port=current_user.smtp_port,
            sender=current_user.email,
            password=password,
            to=data.to,
            cc=data.cc,
            subject=data.subject,
            body=data.body,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to send: {exc}")

    db.add(models.Email(
        user_id=current_user.id,
        message_id=f"sent-{datetime.utcnow().isoformat()}@local",
        subject=data.subject,
        from_addr=current_user.email,
        to_addr=data.to,
        cc_addr=data.cc,
        body_text=data.body,
        date=datetime.utcnow(),
        is_read=True,
        folder="SENT",
    ))
    db.commit()
    return {"status": "sent"}


@router.get("/{email_id}", response_model=schemas.EmailResponse)
def get_email(
    email_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.query(models.Email).filter(
        models.Email.id == email_id,
        models.Email.user_id == current_user.id,
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Email not found")
    if not obj.is_read:
        obj.is_read = True
        db.commit()
    return obj


@router.patch("/{email_id}/read")
def mark_read(
    email_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.query(models.Email).filter(
        models.Email.id == email_id,
        models.Email.user_id == current_user.id,
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Email not found")
    obj.is_read = True
    db.commit()
    return {"status": "ok"}


@router.delete("/{email_id}")
def delete_email(
    email_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obj = db.query(models.Email).filter(
        models.Email.id == email_id,
        models.Email.user_id == current_user.id,
    ).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Email not found")
    db.delete(obj)
    db.commit()
    return {"status": "deleted"}
