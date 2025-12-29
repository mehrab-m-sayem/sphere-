from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
import os


class JWTManager:
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
        Initialize JWT Manager
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: Algorithm for JWT signing
        """
        self.secret_key = secret_key or os.getenv("SECRET_KEY", "SPHERE_SECRET_KEY_CHANGE_IN_PRODUCTION")
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.temp_token_expire_minutes = 5
    
    def create_access_token(
        self, 
        data: Dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            data: Dictionary with user data to encode
            expires_delta: Optional custom expiration time
        
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def create_temp_token(
        self,
        data: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create temporary JWT token (for 2FA)
        
        Args:
            data: Dictionary with data to encode
            expires_delta: Optional custom expiration time
        
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.temp_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "temp"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
        
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def create_refresh_token(
        self,
        data: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create refresh token
        
        Args:
            data: Dictionary with user data
            expires_delta: Optional custom expiration time
        
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt