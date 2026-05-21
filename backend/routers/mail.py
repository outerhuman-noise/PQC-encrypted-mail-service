from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from database import get_db
from crypto.key_storage import decrypt_private_key
from crypto.pqc import encapsulate, sign_message
from crypto.symmetric import encrypt_text

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
    receiver = db.query(models.User).filter(models.User.email == data.to).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    receiver_keys = db.query(models.UserKeys).filter(models.UserKeys.user_id == receiver.id).first()
    sender_keys = db.query(models.UserKeys).filter(models.UserKeys.user_id == current_user.id).first()

    try:
        sender_sign_private = decrypt_private_key(
            sender_keys.sign_private_key_encrypted,
            sender_keys.sign_private_key_nonce,
            sender_keys.sign_private_key_salt,
            data.password,
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Could not unlock your signing key. Check your password.")

    kem_result = encapsulate(receiver_keys["kem_public_key"])

    encrypted = encrypt_text(data.body, kem_result["shared_secret"])

    signed_payload = (encrypted["ciphertext"] + "|" + encrypted["nonce"] + "|" + data.subject).encode("utf-8")
    signature = sign_message(sender_sign_private, signed_payload)

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
        ciphertext=encrypted["ciphertext"],
        nonce=encrypted["nonce"],
        kem_ciphertext=kem_result["kem_ciphertext"],
        signature=signature,
    ))

    db.add(models.Email(
        user_id=receiver.id,
        message_id=f"received-{datetime.utcnow().isoformat()}@local",
        subject=data.subject,
        from_addr=current_user.email,
        to_addr=data.to,
        cc_addr=data.cc,
        date=datetime.utcnow(),
        is_read=False,
        ciphertext=encrypted["ciphertext"],
        nonce=encrypted["nonce"],
        kem_ciphertext=kem_result["kem_ciphertext"],
        signature=signature,
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
