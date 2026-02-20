import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SALT_SIZE = 16
IV_SIZE = 12
KEY_SIZE = 32
ITERATIONS = 200000
MAGIC = b"CVLT1"

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode())

def encrypt_file(input_path: str, output_path: str, password: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError("Input file does not exist.")

    with open(input_path, "rb") as f:
        data = f.read()

    salt = os.urandom(SALT_SIZE)
    iv = os.urandom(IV_SIZE)
    key = derive_key(password, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, data, None)

    with open(output_path, "wb") as f:
        f.write(MAGIC)
        f.write(salt)
        f.write(iv)
        f.write(ciphertext)

def decrypt_file(input_path: str, output_path: str, password: str):
    with open(input_path, "rb") as f:
        magic = f.read(len(MAGIC))
        if magic != MAGIC:
            raise ValueError("Invalid file format.")

        salt = f.read(SALT_SIZE)
        iv = f.read(IV_SIZE)
        ciphertext = f.read()

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(iv, ciphertext, None)
    except Exception:
        raise ValueError("Wrong password or corrupted file.")

    with open(output_path, "wb") as f:
        f.write(plaintext)