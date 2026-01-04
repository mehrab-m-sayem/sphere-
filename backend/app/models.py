"""
Database Models for SPHERE
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base
from app.crypto.rsa import RSA
from app.crypto.ecc import ECC
from app.crypto.mac import HMAC, SHA256
import json
import os
from pathlib import Path


# HMAC key for Message Authentication Codes (used with custom HMAC implementation)
HMAC_KEY = os.getenv("HMAC_SECRET_KEY", "sphere-hmac-secret-key-change-in-production")

# Custom SHA256 instance for hashing (search indexes)
_sha256 = SHA256()


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
    _keys_dir = Path(__file__).parent.parent / "keys"
    
    @classmethod
    def _ensure_keys_dir(cls):
        """Ensure keys directory exists"""
        cls._keys_dir.mkdir(exist_ok=True)
    
    @classmethod
    def _save_rsa_keys(cls, rsa_instance):
        """Save RSA keys to file for persistence"""
        cls._ensure_keys_dir()
        keys_file = cls._keys_dir / "rsa_keys.json"
        keys_data = {
            "public_key": {"e": rsa_instance.public_key[0], "n": rsa_instance.public_key[1]},
            "private_key": {"d": rsa_instance.private_key[0], "n": rsa_instance.private_key[1]}
        }
        with open(keys_file, 'w') as f:
            json.dump(keys_data, f)
        print(f"✅ RSA keys saved to {keys_file}")
    
    @classmethod
    def _load_rsa_keys(cls, rsa_instance) -> bool:
        """Load RSA keys from file. Returns True if loaded successfully."""
        keys_file = cls._keys_dir / "rsa_keys.json"
        if keys_file.exists():
            try:
                with open(keys_file, 'r') as f:
                    keys_data = json.load(f)
                rsa_instance.public_key = (keys_data["public_key"]["e"], keys_data["public_key"]["n"])
                rsa_instance.private_key = (keys_data["private_key"]["d"], keys_data["private_key"]["n"])
                print(f"✅ RSA keys loaded from {keys_file}")
                return True
            except Exception as e:
                print(f"⚠️ Error loading RSA keys: {e}")
        return False
    
    @classmethod
    def _save_ecc_keys(cls, ecc_instance):
        """Save ECC keys to file for persistence"""
        cls._ensure_keys_dir()
        keys_file = cls._keys_dir / "ecc_keys.json"
        keys_data = {
            "public_key": {"x": ecc_instance.public_key.x, "y": ecc_instance.public_key.y},
            "private_key": ecc_instance.private_key
        }
        with open(keys_file, 'w') as f:
            json.dump(keys_data, f)
        print(f"✅ ECC keys saved to {keys_file}")
    
    @classmethod
    def _load_ecc_keys(cls, ecc_instance) -> bool:
        """Load ECC keys from file. Returns True if loaded successfully."""
        keys_file = cls._keys_dir / "ecc_keys.json"
        if keys_file.exists():
            try:
                with open(keys_file, 'r') as f:
                    keys_data = json.load(f)
                from app.crypto.ecc import Point
                ecc_instance.public_key = Point(
                    keys_data["public_key"]["x"],
                    keys_data["public_key"]["y"],
                    ecc_instance.curve
                )
                ecc_instance.private_key = keys_data["private_key"]
                print(f"✅ ECC keys loaded from {keys_file}")
                return True
            except Exception as e:
                print(f"⚠️ Error loading ECC keys: {e}")
        return False
    
    @classmethod
    def get_rsa_instance(cls):
        """Get or create RSA instance with persistent keys"""
        if cls._rsa_instance is None:
            cls._rsa_instance = RSA(key_size=2048)
            # Try to load existing keys, otherwise generate new ones
            if not cls._load_rsa_keys(cls._rsa_instance):
                print("🔑 Generating new RSA keys...")
                cls._rsa_instance.generate_keypair()
                cls._save_rsa_keys(cls._rsa_instance)
        return cls._rsa_instance
    
    @classmethod
    def get_ecc_instance(cls):
        """Get or create ECC instance with persistent keys"""
        if cls._ecc_instance is None:
            cls._ecc_instance = ECC()
            # Try to load existing keys, otherwise generate new ones
            if not cls._load_ecc_keys(cls._ecc_instance):
                print("🔑 Generating new ECC keys...")
                cls._ecc_instance.generate_keypair()
                cls._save_ecc_keys(cls._ecc_instance)
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
                self.username_hash = _sha256.hash_hex(value)
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
                self.email_hash = _sha256.hash_hex(value)
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


class Appointment(Base):
    """
    Appointment Model with Encrypted Fields
    Uses RSA for sensitive fields and HMAC for integrity verification
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys (not encrypted - needed for querying)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Encrypted fields using RSA (reason/notes for appointment)
    reason_encrypted = Column(Text, nullable=False)  # RSA encrypted
    notes_encrypted = Column(Text, nullable=True)  # RSA encrypted (doctor's notes)
    
    # Appointment details (encrypted with ECC)
    appointment_date_encrypted = Column(Text, nullable=False)  # ECC encrypted
    appointment_time_encrypted = Column(Text, nullable=False)  # ECC encrypted
    
    # Status (not encrypted - needed for filtering)
    # pending, confirmed, completed, cancelled
    status = Column(String(20), default="pending")
    
    # HMAC for data integrity verification
    data_hmac = Column(String(64), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="doctor_appointments")
    
    @staticmethod
    def compute_hmac(patient_id: int, doctor_id: int, reason: str, date: str, time: str) -> str:
        """
        Compute HMAC for data integrity verification
        Uses custom HMAC-SHA256 implementation (from scratch) to detect unauthorized modifications
        """
        data = f"{patient_id}:{doctor_id}:{reason}:{date}:{time}"
        hmac_instance = HMAC(HMAC_KEY)
        return hmac_instance.compute_hex(data)
    
    def verify_integrity(self) -> bool:
        """Verify data integrity using custom HMAC implementation"""
        try:
            computed_hmac = self.compute_hmac(
                self.patient_id,
                self.doctor_id,
                self.reason,
                self.appointment_date,
                self.appointment_time
            )
            # Constant-time comparison to prevent timing attacks
            hmac_instance = HMAC(HMAC_KEY)
            return hmac_instance.verify(f"{self.patient_id}:{self.doctor_id}:{self.reason}:{self.appointment_date}:{self.appointment_time}", self.data_hmac)
        except Exception as e:
            print(f"Error verifying HMAC: {e}")
            return False
    
    # ===== RSA Encrypted Fields =====
    
    @property
    def reason(self):
        """Decrypt reason using RSA"""
        if self.reason_encrypted:
            try:
                rsa = User.get_rsa_instance()
                return rsa.decrypt(self.reason_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting reason: {e}")
                return None
        return None
    
    @reason.setter
    def reason(self, value):
        """Encrypt reason using RSA"""
        if value:
            try:
                rsa = User.get_rsa_instance()
                self.reason_encrypted = rsa.encrypt(value, rsa.public_key)
            except Exception as e:
                print(f"Error encrypting reason: {e}")
    
    @property
    def notes(self):
        """Decrypt notes using RSA"""
        if self.notes_encrypted:
            try:
                rsa = User.get_rsa_instance()
                return rsa.decrypt(self.notes_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting notes: {e}")
                return None
        return None
    
    @notes.setter
    def notes(self, value):
        """Encrypt notes using RSA"""
        if value:
            try:
                rsa = User.get_rsa_instance()
                self.notes_encrypted = rsa.encrypt(value, rsa.public_key)
            except Exception as e:
                print(f"Error encrypting notes: {e}")
    
    # ===== ECC Encrypted Fields =====
    
    @property
    def appointment_date(self):
        """Decrypt appointment date using ECC"""
        if self.appointment_date_encrypted:
            try:
                ecc = User.get_ecc_instance()
                return ecc.decrypt(self.appointment_date_encrypted, ecc.private_key)
            except Exception as e:
                print(f"Error decrypting appointment_date: {e}")
                return None
        return None
    
    @appointment_date.setter
    def appointment_date(self, value):
        """Encrypt appointment date using ECC"""
        if value:
            try:
                ecc = User.get_ecc_instance()
                self.appointment_date_encrypted = ecc.encrypt(value, ecc.public_key)
            except Exception as e:
                print(f"Error encrypting appointment_date: {e}")
    
    @property
    def appointment_time(self):
        """Decrypt appointment time using ECC"""
        if self.appointment_time_encrypted:
            try:
                ecc = User.get_ecc_instance()
                return ecc.decrypt(self.appointment_time_encrypted, ecc.private_key)
            except Exception as e:
                print(f"Error decrypting appointment_time: {e}")
                return None
        return None
    
    @appointment_time.setter
    def appointment_time(self, value):
        """Encrypt appointment time using ECC"""
        if value:
            try:
                ecc = User.get_ecc_instance()
                self.appointment_time_encrypted = ecc.encrypt(value, ecc.public_key)
            except Exception as e:
                print(f"Error encrypting appointment_time: {e}")


class Diagnosis(Base):
    """
    Diagnosis Model with Multi-Level Encryption
    Uses RSA for primary fields and ECC for secondary fields
    HMAC ensures data integrity
    """
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys (not encrypted - needed for querying)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    
    # Primary encrypted fields using RSA (sensitive medical data)
    diagnosis_encrypted = Column(Text, nullable=False)  # RSA encrypted - main diagnosis
    prescription_encrypted = Column(Text, nullable=True)  # RSA encrypted - medications
    
    # Secondary encrypted fields using ECC
    symptoms_encrypted = Column(Text, nullable=True)  # ECC encrypted
    notes_encrypted = Column(Text, nullable=True)  # ECC encrypted - additional notes
    
    # Multi-level encryption field (RSA then ECC) - for highly sensitive data
    confidential_notes_encrypted = Column(Text, nullable=True)  # Double encrypted
    
    # HMAC for data integrity verification
    data_hmac = Column(String(64), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id], backref="diagnoses_given")
    patient = relationship("User", foreign_keys=[patient_id], backref="diagnoses_received")
    appointment = relationship("Appointment", backref="diagnosis")
    
    @staticmethod
    def compute_hmac(doctor_id: int, patient_id: int, diagnosis: str, prescription: str = "") -> str:
        """
        Compute HMAC for data integrity verification
        Uses custom HMAC-SHA256 implementation (from scratch) to detect unauthorized modifications
        """
        data = f"{doctor_id}:{patient_id}:{diagnosis}:{prescription}"
        hmac_instance = HMAC(HMAC_KEY)
        return hmac_instance.compute_hex(data)
    
    def verify_integrity(self) -> bool:
        """Verify data integrity using custom HMAC implementation"""
        try:
            data = f"{self.doctor_id}:{self.patient_id}:{self.diagnosis or ''}:{self.prescription or ''}"
            hmac_instance = HMAC(HMAC_KEY)
            return hmac_instance.verify(data, self.data_hmac)
        except Exception as e:
            print(f"Error verifying diagnosis HMAC: {e}")
            return False
    
    # ===== RSA Encrypted Fields (Primary Medical Data) =====
    
    @property
    def diagnosis(self):
        """Decrypt diagnosis using RSA"""
        if self.diagnosis_encrypted:
            try:
                rsa = User.get_rsa_instance()
                return rsa.decrypt(self.diagnosis_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting diagnosis: {e}")
                return None
        return None
    
    @diagnosis.setter
    def diagnosis(self, value):
        """Encrypt diagnosis using RSA"""
        if value:
            try:
                rsa = User.get_rsa_instance()
                self.diagnosis_encrypted = rsa.encrypt(value, rsa.public_key)
            except Exception as e:
                print(f"Error encrypting diagnosis: {e}")
    
    @property
    def prescription(self):
        """Decrypt prescription using RSA"""
        if self.prescription_encrypted:
            try:
                rsa = User.get_rsa_instance()
                return rsa.decrypt(self.prescription_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting prescription: {e}")
                return None
        return None
    
    @prescription.setter
    def prescription(self, value):
        """Encrypt prescription using RSA"""
        if value:
            try:
                rsa = User.get_rsa_instance()
                self.prescription_encrypted = rsa.encrypt(value, rsa.public_key)
            except Exception as e:
                print(f"Error encrypting prescription: {e}")
    
    # ===== ECC Encrypted Fields (Secondary Data) =====
    
    @property
    def symptoms(self):
        """Decrypt symptoms using ECC"""
        if self.symptoms_encrypted:
            try:
                ecc = User.get_ecc_instance()
                return ecc.decrypt(self.symptoms_encrypted, ecc.private_key)
            except Exception as e:
                print(f"Error decrypting symptoms: {e}")
                return None
        return None
    
    @symptoms.setter
    def symptoms(self, value):
        """Encrypt symptoms using ECC"""
        if value:
            try:
                ecc = User.get_ecc_instance()
                self.symptoms_encrypted = ecc.encrypt(value, ecc.public_key)
            except Exception as e:
                print(f"Error encrypting symptoms: {e}")
    
    @property
    def notes(self):
        """Decrypt notes using ECC"""
        if self.notes_encrypted:
            try:
                ecc = User.get_ecc_instance()
                return ecc.decrypt(self.notes_encrypted, ecc.private_key)
            except Exception as e:
                print(f"Error decrypting diagnosis notes: {e}")
                return None
        return None
    
    @notes.setter
    def notes(self, value):
        """Encrypt notes using ECC"""
        if value:
            try:
                ecc = User.get_ecc_instance()
                self.notes_encrypted = ecc.encrypt(value, ecc.public_key)
            except Exception as e:
                print(f"Error encrypting diagnosis notes: {e}")
    
    # ===== Multi-Level Encryption (RSA + ECC) =====
    
    @property
    def confidential_notes(self):
        """
        Decrypt confidential notes using multi-level decryption
        First decrypt ECC layer, then RSA layer
        """
        if self.confidential_notes_encrypted:
            try:
                ecc = User.get_ecc_instance()
                rsa = User.get_rsa_instance()
                # First decrypt ECC layer
                rsa_encrypted = ecc.decrypt(self.confidential_notes_encrypted, ecc.private_key)
                # Then decrypt RSA layer
                return rsa.decrypt(rsa_encrypted, rsa.private_key)
            except Exception as e:
                print(f"Error decrypting confidential notes: {e}")
                return None
        return None
    
    @confidential_notes.setter
    def confidential_notes(self, value):
        """
        Encrypt confidential notes using multi-level encryption
        First encrypt with RSA, then encrypt result with ECC
        """
        if value:
            try:
                rsa = User.get_rsa_instance()
                ecc = User.get_ecc_instance()
                # First encrypt with RSA
                rsa_encrypted = rsa.encrypt(value, rsa.public_key)
                # Then encrypt with ECC
                self.confidential_notes_encrypted = ecc.encrypt(rsa_encrypted, ecc.public_key)
            except Exception as e:
                print(f"Error encrypting confidential notes: {e}")