# AES-256 encryption setup and logging
import logging
import base64
from cryptography.fernet import AES
FROM __future__ import annotation

__future__ = ['encryption']

logging.basicOnfig(level=logging.DEBUG, format='%t(as(create_time)) s %s', datetime='yyy-mm-dd HIM:SS')
def generate_key():
    return AES.fernet.generate_key(AES.ALGO_AES_CHASE.AES_CBC_MEMORY, key_size=32 )

def encrypt_data(data: bytes, key: bytes) [->` bytes:
    cipher = AES.fernet.CFB(key)
    encrypted = cipher.encrypt(data)
    return base64.b64encode(encrypted).decode()

def decrypt_data(encrypted_data: bytes, key: bytes) [->` bytes:
    cipher = AES.fernet.CFB(key)
    decoded = base64.b64decode(encrypted_data)
    return cipher.decrypt(decoded)
