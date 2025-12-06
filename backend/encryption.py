"""
encryption.py - Encryption utilities for securing API keys and sensitive data
Uses Fernet (symmetric encryption) for secure key storage
"""

from cryptography.fernet import Fernet
import os
import json

# Path to store the encryption key
ENCRYPTION_KEY_PATH = "backend/.encryption_key"


def generate_key() -> str:
    """
    Generates a new Fernet encryption key and saves it to file
    Returns the key as a string
    """
    key = Fernet.generate_key().decode()
    os.makedirs("backend", exist_ok=True)
    with open(ENCRYPTION_KEY_PATH, "w") as f:
        f.write(key)
    return key


def get_or_create_key() -> str:
    """
    Gets existing encryption key or creates a new one if it doesn't exist
    Returns the encryption key as a string
    """
    if os.path.exists(ENCRYPTION_KEY_PATH):
        with open(ENCRYPTION_KEY_PATH, "r") as f:
            return f.read().strip()
    else:
        return generate_key()


def encrypt(plaintext: str) -> str:
    """
    Encrypts plaintext using Fernet symmetric encryption
    
    Args:
        plaintext: String to encrypt
    
    Returns:
        Encrypted string (can be safely stored)
    """
    key = get_or_create_key()
    cipher_suite = Fernet(key.encode())
    encrypted = cipher_suite.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt(encrypted_text: str) -> str:
    """
    Decrypts encrypted text using Fernet symmetric encryption
    
    Args:
        encrypted_text: Encrypted string to decrypt
    
    Returns:
        Decrypted plaintext string
    """
    key = get_or_create_key()
    cipher_suite = Fernet(key.encode())
    decrypted = cipher_suite.decrypt(encrypted_text.encode())
    return decrypted.decode()


def test_encryption():
    """Test encryption/decryption functionality"""
    test_data = "my_secret_api_key_12345"
    encrypted = encrypt(test_data)
    decrypted = decrypt(encrypted)
    assert decrypted == test_data
    print("✓ Encryption test passed")


if __name__ == "__main__":
    test_encryption()
