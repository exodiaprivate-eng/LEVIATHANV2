"""API key encryption utilities."""
import logging
from pathlib import Path

logger = logging.getLogger('leviathan.encryption')


def encrypt_key(plaintext: str, key_path: str = '.leviathan_key') -> bytes:
    from cryptography.fernet import Fernet
    kp = Path(key_path)
    if not kp.exists():
        key = Fernet.generate_key()
        kp.write_bytes(key)
    else:
        key = kp.read_bytes()
    return Fernet(key).encrypt(plaintext.encode())


def decrypt_key(ciphertext: bytes, key_path: str = '.leviathan_key') -> str:
    from cryptography.fernet import Fernet
    key = Path(key_path).read_bytes()
    return Fernet(key).decrypt(ciphertext).decode()
