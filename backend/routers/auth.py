from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_db
from crypto.key_storage import encrypt_private_key
from crypto.pqc import generate_kem_keypair, generate_sign_keypair

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.flush()  # assigns user.id before we reference it in UserKeys

    kem = generate_kem_keypair()
    sig = generate_sign_keypair()
    enc_kem = encrypt_private_key(kem["private_key"], data.password)
    enc_sig = encrypt_private_key(sig["private_key"], data.password)

    db.add(models.UserKeys(
        user_id=user.id,
        kem_public_key=kem["public_key"],
        kem_private_key_encrypted=enc_kem["encrypted"],
        kem_private_key_nonce=enc_kem["nonce"],
        kem_private_key_salt=enc_kem["salt"],
        sign_public_key=sig["public_key"],
        sign_private_key_encrypted=enc_sig["encrypted"],
        sign_private_key_nonce=enc_sig["nonce"],
        sign_private_key_salt=enc_sig["salt"],
    ))
    
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
