import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.getenv("FERNET_KEY")
        if not key:
            key = Fernet.generate_key().decode()
            print(f"WARNING: FERNET_KEY not set. Set this in .env:\nFERNET_KEY={key}")
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_password(password: str) -> str:
    return _get_fernet().encrypt(password.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()
