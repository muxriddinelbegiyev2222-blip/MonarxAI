"""MonarxAI — Parolni hashlash va shifrlash moduli."""
import os
import base64
import hashlib
import hmac
from cryptography.fernet import Fernet

PBKDF2_ROUNDS = 310_000
ALGO = "pbkdf2_sha256"


def hash_parol(parol: str, salt: bytes = None) -> str:
    """Parolni PBKDF2-HMAC-SHA256 bilan hashlaydi."""
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", parol.encode(), salt, PBKDF2_ROUNDS)
    return f"{ALGO}${PBKDF2_ROUNDS}${salt.hex()}${dk.hex()}"


def tekshir_parol(parol: str, saqlangan: str) -> bool:
    """Kiritilgan parolni saqlangan hash bilan solishtiradi."""
    try:
        algo, rounds_s, salt_hex, hash_hex = saqlangan.split("$")
        if algo != ALGO:
            return False
        rounds = int(rounds_s)
        salt = bytes.fromhex(salt_hex)
        kutilgan = bytes.fromhex(hash_hex)
        dk = hashlib.pbkdf2_hmac("sha256", parol.encode(), salt, rounds)
        return hmac.compare_digest(dk, kutilgan)
    except (ValueError, AttributeError):
        return False


def kalit_yarat(parol: str, salt: bytes) -> bytes:
    """Paroldan shifrlash kaliti yasaydi."""
    dk = hashlib.pbkdf2_hmac("sha256", parol.encode(), salt, PBKDF2_ROUNDS)
    return base64.urlsafe_b64encode(dk)


def shifrla(parol: str, salt: bytes, malumot: str) -> bytes:
    """Ma'lumotni Fernet bilan shifrlaydi."""
    f = Fernet(kalit_yarat(parol, salt))
    return f.encrypt(malumot.encode())


def deshifrla(parol: str, salt: bytes, shifrlangan: bytes) -> str:
    """Shifrlangan ma'lumotni ochadi."""
    f = Fernet(kalit_yarat(parol, salt))
    return f.decrypt(shifrlangan).decode()
