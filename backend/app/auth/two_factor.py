"""
Two-Factor Authentication Module
SPHERE - Secure Patient Health Record System
"""

import random
import string


class TwoFactorAuth:
    """Handles two-factor authentication"""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """
        Generate random 6-digit code
        
        Args:
            length: Code length
        
        Returns:
            Random digit string
        """
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def verify_code(provided_code: str, stored_code: str) -> bool:
        """
        Verify provided code against stored code
        
        Args:
            provided_code: Code provided by user
            stored_code: Code stored in token
        
        Returns:
            True if codes match
        """
        return provided_code == stored_code