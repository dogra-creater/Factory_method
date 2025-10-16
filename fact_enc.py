# encrypt_config.py
import json
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

def derive_key_from_passphrase(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

def encrypt_config(passphrase: str):
    credentials = {
        "camera_1": {
            "type": "ipcamera",
            "ip": "192.168.31.68",
            "user": "admin",
            "password": "Mypassword@25"
        },
        "camera_2": {
            "type": "cpplus",
            "ip": "192.168.31.70",
            "user": "admin",
            "password": "Mypassword@25"
        }
    }

    json_data = json.dumps(credentials).encode()

    salt = os.urandom(16)
    key = derive_key_from_passphrase(passphrase, salt)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json_data)

    with open("config.enc", "wb") as f:
        f.write(salt + encrypted_data)

    print("✅ Config encrypted and saved as config.enc")

if __name__ == "__main__":
    passphrase = input("Enter passphrase to encrypt credentials: ")
    encrypt_config(passphrase)
