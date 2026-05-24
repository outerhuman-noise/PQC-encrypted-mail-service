import os
from crypto.encoding import b64, unb64

KEM_ALG = os.getenv("KEM_ALG", "ML-KEM-768")
SIG_ALG = os.getenv("SIG_ALG", "ML-DSA-65")

try:
    import oqs
except Exception as exc:  # pragma: no cover
    oqs = None
    OQS_IMPORT_ERROR = exc
else:
    OQS_IMPORT_ERROR = None


def require_oqs():
    if oqs is None:
        raise RuntimeError(
            "liboqs-python is installed but native liboqs is not available. "
            "Install liboqs shared libraries and ensure LD_LIBRARY_PATH includes the install lib folder. "
            f"Original error: {OQS_IMPORT_ERROR}"
        )


def enabled_algorithms():
    require_oqs()
    return {
        "oqs_version": oqs.oqs_version(),
        "enabled_kems": oqs.get_enabled_kem_mechanisms(),
        "enabled_signatures": oqs.get_enabled_sig_mechanisms(),
        "selected_kem": KEM_ALG,
        "selected_signature": SIG_ALG,
    }


def generate_kem_keypair():
    require_oqs()
    with oqs.KeyEncapsulation(KEM_ALG) as kem:
        public_key = kem.generate_keypair()
        private_key = kem.export_secret_key()
    return {"public_key": b64(public_key), "private_key": b64(private_key)}


def encapsulate(receiver_public_key_b64: str):
    require_oqs()
    with oqs.KeyEncapsulation(KEM_ALG) as kem:
        ciphertext, shared_secret = kem.encap_secret(unb64(receiver_public_key_b64))
    return {"kem_ciphertext": b64(ciphertext), "shared_secret": shared_secret}


def decapsulate(receiver_private_key_b64: str, kem_ciphertext_b64: str):
    require_oqs()
    with oqs.KeyEncapsulation(KEM_ALG, secret_key=unb64(receiver_private_key_b64)) as kem:
        return kem.decap_secret(unb64(kem_ciphertext_b64))


def generate_sign_keypair():
    require_oqs()
    with oqs.Signature(SIG_ALG) as sig:
        public_key = sig.generate_keypair()
        private_key = sig.export_secret_key()
    return {"public_key": b64(public_key), "private_key": b64(private_key)}


def sign_message(private_key_b64: str, message: bytes) -> str:
    require_oqs()
    with oqs.Signature(SIG_ALG, secret_key=unb64(private_key_b64)) as sig:
        return b64(sig.sign(message))


def verify_signature(public_key_b64: str, message: bytes, signature_b64: str) -> bool:
    require_oqs()
    with oqs.Signature(SIG_ALG) as sig:
        return bool(sig.verify(message, unb64(signature_b64), unb64(public_key_b64)))
