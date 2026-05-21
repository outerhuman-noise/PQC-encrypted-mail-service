from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class EmailResponse(BaseModel):
    id: int
    message_id: Optional[str]
    subject: str
    from_addr: str
    to_addr: str
    cc_addr: str
    body_text: str
    body_html: str
    date: Optional[datetime]
    is_read: bool
    folder: str
    ciphertext: Optional[str]
    nonce: Optional[str]
    kem_ciphertext: Optional[str]
    signature: Optional[str]

    model_config = {"from_attributes": True}


class SendEmailRequest(BaseModel):
    to: str
    cc: str = ""
    subject: str
    body: str
    password: str


class DecryptRequest(BaseModel):
    password: str


class DecryptResponse(BaseModel):
    body: str
    verified: bool
