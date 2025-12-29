"""
Password Hashing Module
SPHERE - Secure Patient Health Record System

Uses SHA256 with salt for password hashing
"""

import hashlib
import secrets


class PasswordManager:
    """Handles password hashing, salting, and verification"""
    
    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """Generate a cryptographic salt"""
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with SHA256 and salt"""
        salt = PasswordManager.generate_salt()
        password_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        return f"{salt}${password_hash}"
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = hashed_password.split('$')
            computed_hash = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
            return computed_hash == stored_hash
        except Exception:
            return False