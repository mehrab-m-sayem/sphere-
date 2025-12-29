"""
Database Models for SPHERE
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base
from app.crypto.rsa import RSA
from app.crypto.ecc import ECC
import hashlib


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Encrypted fields using RSA
    username_encrypted = Column(Text, nullable=False)  # RSA encrypted
    email_encrypted = Column(Text, nullable=False)  # RSA encrypted
    name_encrypted = Column(Text, nullable=False)  # RSA encrypted
    contact_no_encrypted = Column(Text, nullable=True)  # RSA encrypted
    
    # Hash indexes for searching (SHA256 hash, not encrypted)
    username_hash = Column(String(64), unique=True, index=True, nullable=False)
    email_hash = Column(String(64), unique=True, index=True, nullable=False)
    
    # Password (already hashed with SHA256+salt)
    hashed_password = Column(String(255), nullable=False)
    
    # Role and status
    role = Column(String(20), default="patient")  # admin, doctor, patient
    is_active = Column(Boolean, default=True)
    
    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255), nullable=True)
    
    # Doctor specific - encrypted using ECC
    specialization_encrypted = Column(Text, nullable=True)  # ECC encrypted
    
    # Patient specific - encrypted using ECC
    age_encrypted = Column(Text, nullable=True)  # ECC encrypted
    sex_encrypted = Column(Text, nullable=True)  # ECC encrypted
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Initialize RSA and ECC globally (one instance per app)
    _rsa_instance = None
    _ecc_instance = None
    
    @classmethod
    def get_rsa_instance(cls):
        """Get or create RSA instance"""
        if cls._rsa_instance is None:
            cls._rsa_instance = RSA(key_size=2048)
            # Generate keypair immediately
            cls._rsa_instance.generate_keypair()
        return cls._rsa_instance
    
    @classmethod
    def get_ecc_instance(cls):
        """Get or create ECC instance"""
        if cls._ecc_instance is None:
            cls._ecc_instance = ECC()
            cls._ecc_instance.generate_keypair()
        return cls._ecc_instance
    
    # ===== RSA Encrypted Fields (Username, Email, Name, Contact) =====
    
    @property
    def username(self):
        """Decrypt username using RSA"""
        if self.username_encrypted:
            try:
                rsa = self.get_rsa_instance()
                return rsa.decrypt(self.username_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting username: {e}")
                return None
        return None
    
    @username.setter
    def username(self, value):
        """Encrypt username using RSA"""
        if value:
            try:
                rsa = self.get_rsa_instance()
                self.username_encrypted = rsa.encrypt(value, rsa.public_key)
                self.username_hash = hashlib.sha256(value.encode()).hexdigest()
            except Exception as e:
                print(f"Error encrypting username: {e}")
    
    @property
    def email(self):
        """Decrypt email using RSA"""
        if self.email_encrypted:
            try:
                rsa = self.get_rsa_instance()
                return rsa.decrypt(self.email_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting email: {e}")
                return None
        return None
    
    @email.setter
    def email(self, value):
        """Encrypt email using RSA"""
        if value:
            try:
                rsa = self.get_rsa_instance()
                self.email_encrypted = rsa.encrypt(value, rsa.public_key)
                self.email_hash = hashlib.sha256(value.encode()).hexdigest()
            except Exception as e:
                print(f"Error encrypting email: {e}")
    
    @property
    def name(self):
        """Decrypt name using RSA"""
        if self.name_encrypted:
            try:
                rsa = self.get_rsa_instance()
                return rsa.decrypt(self.name_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting name: {e}")
                return None
        return None
    
    @name.setter
    def name(self, value):
        """Encrypt name using RSA"""
        if value:
            try:
                rsa = self.get_rsa_instance()
                self.name_encrypted = rsa.encrypt(value, rsa.public_key)
            except Exception as e:
                print(f"Error encrypting name: {e}")
    
    @property
    def contact_no(self):
        """Decrypt contact number using RSA"""
        if self.contact_no_encrypted:
            try:
                rsa = self.get_rsa_instance()
                return rsa.decrypt(self.contact_no_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting contact_no: {e}")
                return None
        return None
    
    @contact_no.setter
    def contact_no(self, value):
        """Encrypt contact number using RSA"""
        if value:
            try:
                rsa = self.get_rsa_instance()
                self.contact_no_encrypted = rsa.encrypt(value, rsa.public_key)
            except Exception as e:
                print(f"Error encrypting contact_no: {e}")
    
    # ===== ECC Encrypted Fields (Specialization, Age, Sex) =====
    
    @property
    def specialization(self):
        """Decrypt specialization using ECC"""
        if self.specialization_encrypted:
            try:
                ecc = self.get_ecc_instance()
                return ecc.decrypt(self.specialization_encrypted, ecc.private_key)
            except Exception as e:
                print(f"Error decrypting specialization: {e}")
                return None
        return None
    
    @specialization.setter
    def specialization(self, value):
        """Encrypt specialization using ECC"""
        if value:
            try:
                ecc = self.get_ecc_instance()
                self.specialization_encrypted = ecc.encrypt(value, ecc.public_key)
            except Exception as e:
                print(f"Error encrypting specialization: {e}")
    
    @property
    def age(self):
        """Decrypt age using ECC"""
        if self.age_encrypted:
            try:
                ecc = self.get_ecc_instance()
                age_str = ecc.decrypt(self.age_encrypted, ecc.private_key)
                return int(age_str) if age_str else None
            except Exception as e:
                print(f"Error decrypting age: {e}")
                return None
        return None
    
    @age.setter
    def age(self, value):
        """Encrypt age using ECC"""
        if value is not None:
            try:
                ecc = self.get_ecc_instance()
                self.age_encrypted = ecc.encrypt(str(value), ecc.public_key)
            except Exception as e:
                print(f"Error encrypting age: {e}")
    
    @property
    def sex(self):
        """Decrypt sex using ECC"""
        if self.sex_encrypted:
            try:
                ecc = self.get_ecc_instance()
                return ecc.decrypt(self.sex_encrypted, ecc.private_key)
            except Exception as e:
                print(f"Error decrypting sex: {e}")
                return None
        return None
    
    @sex.setter
    def sex(self, value):
        """Encrypt sex using ECC"""
        if value:
            try:
                ecc = self.get_ecc_instance()
                self.sex_encrypted = ecc.encrypt(value, ecc.public_key)
            except Exception as e:
                print(f"Error encrypting sex: {e}")