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
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


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