from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    emails = relationship("Email", back_populates="user", cascade="all, delete-orphan")
    keys = relationship("UserKeys", back_populates="user", cascade="all, delete-orphan")

class UserKeys(Base):
    __tablename__ = "user_keys"

    id = Column(Integer, primary_key=True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    kem_public_key = Column(Text, nullable=False)
    kem_private_key_encrypted = Column(Text, nullable=False)
    kem_private_key_nonce = Column(Text, nullable=False)
    kem_private_key_salt = Column(Text, nullable=False)
    
    sign_public_key = Column(Text, nullable=False)
    sign_private_key_encrypted = Column(Text, nullable=False)
    sign_private_key_nonce = Column(Text, nullable=False)
    sign_private_key_salt = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="keys")

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_id = Column(String, index=True)
    uid = Column(String)
    subject = Column(String, default="(no subject)")
    from_addr = Column(String, default="")
    to_addr = Column(String, default="")
    cc_addr = Column(String, default="")
    body_text = Column(Text, default="")
    body_html = Column(Text, default="")
    date = Column(DateTime)
    is_read = Column(Boolean, default=False)
    folder = Column(String, default="INBOX")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="emails")
