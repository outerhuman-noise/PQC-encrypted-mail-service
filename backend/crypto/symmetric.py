from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
from app.crypto.encoding import b64, unb64


def encrypt_text(plaintext: str, key: bytes):
    aes_key = key[:32]
    nonce = os.urandom(12)
    ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext.encode("utf-8"), None)
    return {"ciphertext": b64(ciphertext), "nonce": b64(nonce)}


def decrypt_text(ciphertext_b64: str, nonce_b64: str, key: bytes):
    aes_key = key[:32]
    plaintext = AESGCM(aes_key).decrypt(unb64(nonce_b64), unb64(ciphertext_b64), None)
    return plaintext.decode("utf-8")
