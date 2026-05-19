import base64
import hashlib
import os
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ph = PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(hash_value: str, password: str) -> bool:
    try:
        return ph.verify(hash_value, password)
    except Exception:
        return False


def derive_key(password: str, salt_b64: str) -> bytes:
    salt = base64.b64decode(salt_b64.encode("utf-8"))
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 250000, dklen=32)


def encrypt_private_key(private_key_b64: str, password: str):
    salt = os.urandom(16)
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    key = derive_key(password, salt_b64)
    nonce = os.urandom(12)
    encrypted = AESGCM(key).encrypt(nonce, private_key_b64.encode("utf-8"), None)
    return {
        "encrypted": base64.b64encode(encrypted).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "salt": salt_b64,
    }


def decrypt_private_key(encrypted_b64: str, nonce_b64: str, salt_b64: str, password: str) -> str:
    key = derive_key(password, salt_b64)
    plaintext = AESGCM(key).decrypt(
        base64.b64decode(nonce_b64.encode("utf-8")),
        base64.b64decode(encrypted_b64.encode("utf-8")),
        None,
    )
    return plaintext.decode("utf-8")
