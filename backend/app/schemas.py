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