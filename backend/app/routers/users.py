
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


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