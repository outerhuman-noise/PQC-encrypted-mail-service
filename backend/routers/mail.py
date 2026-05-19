from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/mail", tags=["mail"])


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
def send_mail(
    data: schemas.SendEmailRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
