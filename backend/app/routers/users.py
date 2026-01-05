
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, DoctorPublicInfo, TwoFactorToggle, PasswordChange
from app.dependencies import get_current_user
from app.auth.password import PasswordManager

router = APIRouter(prefix="/api/users", tags=["users"])
password_manager = PasswordManager()


@router.get("/doctors", response_model=List[DoctorPublicInfo])
async def get_doctors_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get list of all registered doctors with their specializations.
    Available to all authenticated users (patients can view doctors).
    Data is automatically decrypted via model properties.
    """
    doctors = db.query(User).filter(
        User.role == "doctor",
        User.is_active == True
    ).all()
    
    # Return decrypted doctor information
    # The model properties handle automatic decryption
    return [
        DoctorPublicInfo(
            id=doctor.id,
            name=doctor.name,  # Decrypted via RSA
            specialization=doctor.specialization  # Decrypted via ECC
        )
        for doctor in doctors
    ]


@router.get("/me", response_model=UserResponse)
async def get_current_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_profile(
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user profile"""
    
    # Update allowed fields
    allowed_fields = ["name", "contact_no", "specialization"]
    
    for field, value in update_data.items():
        if field in allowed_fields and value is not None:
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.put("/me/password", response_model=UserResponse)
async def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change user password.
    Uses SHA256 with salt for password hashing (cryptographic requirement).
    """
    
    # Validate new password matches confirmation
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # Verify current password
    if not password_manager.verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength (minimum requirements)
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Hash new password with SHA256 + salt
    new_hashed_password = password_manager.hash_password(data.new_password)
    current_user.hashed_password = new_hashed_password
    
    db.commit()
    db.refresh(current_user)
    
    print(f"Password changed for user: {current_user.email}")
    
    return current_user


@router.put("/me/2fa", response_model=UserResponse)
async def toggle_two_factor(
    data: TwoFactorToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle two-factor authentication for current user"""
    
    current_user.two_factor_enabled = data.enabled
    db.commit()
    db.refresh(current_user)
    
    status_text = "enabled" if data.enabled else "disabled"
    print(f"2FA {status_text} for user: {current_user.email}")
    
    return current_user