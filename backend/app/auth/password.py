"""
Password Hashing Module
Uses custom SHA256 implementation with salt for password hashing
"""

import secrets
from app.crypto.mac import SHA256


class PasswordManager:
    """Handles password hashing, salting, and verification"""
    
    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """Generate a cryptographic salt"""
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with custom SHA256 implementation and salt"""
        salt = PasswordManager.generate_salt()
        sha256 = SHA256()
        password_hash = sha256.hash_hex(salt + password)
        return f"{salt}${password_hash}"
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash using custom SHA256"""
        try:
            salt, stored_hash = hashed_password.split('$')
            sha256 = SHA256()
            computed_hash = sha256.hash_hex(salt + plain_password)
            # Constant-time comparison to prevent timing attacks
            if len(computed_hash) != len(stored_hash):
                return False
            result = 0
            for a, b in zip(computed_hash, stored_hash):
                result |= ord(a) ^ ord(b)
            return result == 0
        except Exception:
            return False