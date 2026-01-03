
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, DoctorPublicInfo
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


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
    allowed_fields = ["name", "contact_no", specialization]
    
    for field, value in update_data.items():
        if field in allowed_fields and value is not None:
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user