"""
Pydantic Schemas for SPHERE
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    contact_no: Optional[str] = None


class DoctorRegister(UserBase):
    password: str
    confirm_password: str
    specialization: str


class PatientRegister(UserBase):
    password: str
    confirm_password: str
    age: int
    sex: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: str
    role: str
    contact_no: Optional[str]
    specialization: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    is_active: bool
    two_factor_enabled: bool = True
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class TwoFactorToggle(BaseModel):
    enabled: bool


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordVerify(BaseModel):
    temp_token: str
    code: str
    new_password: str
    confirm_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    requires_2fa: bool = False
    temp_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class TwoFAVerify(BaseModel):
    temp_token: str
    code: str


class DoctorPublicInfo(BaseModel):
    """Public doctor information visible to patients"""
    id: int
    name: str
    specialization: Optional[str]
    
    class Config:
        from_attributes = True


# ===== Appointment Schemas =====

class AppointmentCreate(BaseModel):
    """Schema for creating an appointment"""
    doctor_id: int
    appointment_date: str  # Format: YYYY-MM-DD
    appointment_time: str  # Format: HH:MM
    reason: str


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    status: Optional[str] = None  # pending, confirmed, completed, cancelled
    notes: Optional[str] = None  # Doctor's notes
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Schema for appointment response"""
    id: int
    patient_id: int
    doctor_id: int
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    appointment_date: Optional[str]
    appointment_time: Optional[str]
    reason: Optional[str]
    notes: Optional[str] = None
    status: str
    integrity_verified: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== Diagnosis Schemas =====

class DiagnosisCreate(BaseModel):
    """Schema for creating a diagnosis"""
    patient_id: int
    appointment_id: Optional[int] = None
    diagnosis: str
    prescription: Optional[str] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    confidential_notes: Optional[str] = None  # Multi-level encrypted


class DiagnosisUpdate(BaseModel):
    """Schema for updating a diagnosis"""
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    confidential_notes: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """Schema for diagnosis response"""
    id: int
    doctor_id: int
    patient_id: int
    appointment_id: Optional[int] = None
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None
    diagnosis: Optional[str]
    prescription: Optional[str] = None
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    confidential_notes: Optional[str] = None
    integrity_verified: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PatientListItem(BaseModel):
    """Schema for patient list visible to doctors"""
    id: int
    name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    
    class Config:
        from_attributes = True