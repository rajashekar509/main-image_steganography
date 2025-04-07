from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def _derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data: str, password: str) -> str:
    key, salt = _derive_key(password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    result = base64.urlsafe_b64encode(salt + encrypted).decode()
    print(f"Encrypted Data: {result}")
    return result

def decrypt_data(encrypted_data: str, password: str) -> str:
    decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
    salt = decoded_data[:16]
    encrypted = decoded_data[16:]
    key, _ = _derive_key(password, salt)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted).decode()
    print(f"Decrypted Data: {decrypted}")
    return decrypted