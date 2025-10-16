# main.py
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from factory import CameraFactory
import threading

# -------------------------------
# Derive key from passphrase
# -------------------------------
def derive_key_from_passphrase(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))

# -------------------------------
# Decrypt config
# -------------------------------
def decrypt_config(passphrase: str, file_path="config.enc"):
    with open(file_path, "rb") as f:
        file_data = f.read()

    salt = file_data[:16]
    encrypted_data = file_data[16:]

    key = derive_key_from_passphrase(passphrase, salt)
    fernet = Fernet(key)

    decrypted_data = fernet.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())

# -------------------------------
# Function to run each camera
# -------------------------------
def run_camera(cam_key, cam_info):
    camera_type = cam_info.get("type")
    ip = cam_info.get("ip")
    user = cam_info.get("user")
    password = cam_info.get("password")

    if not all([camera_type, ip, user, password]):
        print(f"❌ Missing fields for {cam_key}, skipping...")
        return

    print(f"\n=== Connecting to {cam_key} ({camera_type}) ===")
    camera_instance = CameraFactory.get_camera(camera_type, ip, user, password)
    camera_instance.connect()
    camera_instance.get_feed()  # Opens live OpenCV stream window

# -------------------------------
# Main logic
# -------------------------------
def main():
    print("=== Secure Camera Connection System ===")
    passphrase = input("🔐 Enter passphrase to decrypt credentials: ")

    try:
        config = decrypt_config(passphrase)
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return

    threads = []

    # Start a thread for each camera
    for cam_key in sorted(config.keys()):
        cam_info = config[cam_key]
        t = threading.Thread(target=run_camera, args=(cam_key, cam_info))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("\n✅ All camera feeds initialized successfully.")

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    main()
